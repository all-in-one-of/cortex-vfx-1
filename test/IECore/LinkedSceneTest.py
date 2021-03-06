##########################################################################
#
#  Copyright (c) 2013, Image Engine Design Inc. All rights reserved.
#
#  Redistribution and use in source and binary forms, with or without
#  modification, are permitted provided that the following conditions are
#  met:
#
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#
#     * Neither the name of Image Engine Design nor the names of any
#       other contributors to this software may be used to endorse or
#       promote products derived from this software without specific prior
#       written permission.
#
#  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS
#  IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
#  THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
#  PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR
#  CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
#  EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
#  PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
#  PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
#  LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
#  NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
#  SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
##########################################################################

import gc
import sys
import math
import unittest

import IECore

class LinkedSceneTest( unittest.TestCase ) :

	@staticmethod
	def compareBBox( box1, box2 ):
		errorTolerance = IECore.V3d(1e-5, 1e-5, 1e-5)
		boxTmp = IECore.Box3d( box1.min - errorTolerance, box1.max + errorTolerance )
		if not boxTmp.contains( box2 ):
			return False
		boxTmp = IECore.Box3d( box2.min - errorTolerance, box2.max + errorTolerance )
		if not boxTmp.contains( box1 ):
			return False
		return True
	
	def testSupportedExtension( self ) :
		self.assertTrue( "lscc" in IECore.SceneInterface.supportedExtensions() )
		self.assertTrue( "lscc" in IECore.SceneInterface.supportedExtensions( IECore.IndexedIO.OpenMode.Read ) )
		self.assertTrue( "lscc" in IECore.SceneInterface.supportedExtensions( IECore.IndexedIO.OpenMode.Write ) )
		self.assertTrue( "lscc" in IECore.SceneInterface.supportedExtensions( IECore.IndexedIO.OpenMode.Write + IECore.IndexedIO.OpenMode.Read ) )
		self.assertFalse( "lscc" in IECore.SceneInterface.supportedExtensions( IECore.IndexedIO.OpenMode.Append ) )

	def testFactoryFunction( self ):
		# test Write factory function 
		m = IECore.SceneInterface.create( "/tmp/test.lscc", IECore.IndexedIO.OpenMode.Write )
		self.assertTrue( isinstance( m, IECore.LinkedScene ) )
		self.assertEqual( m.fileName(), "/tmp/test.lscc" )
		self.assertRaises( RuntimeError, m.readBound, 0.0 )
		del m
		# test Read factory function
		m = IECore.SceneInterface.create( "/tmp/test.lscc", IECore.IndexedIO.OpenMode.Read )
		self.assertTrue( isinstance( m, IECore.LinkedScene ) )
		self.assertEqual( m.fileName(), "/tmp/test.lscc" )
		m.readBound( 0.0 )

	def testConstructors( self ):

		# test Read from a previously opened scene.
		m = IECore.SceneCache( "test/IECore/data/sccFiles/animatedSpheres.scc", IECore.IndexedIO.OpenMode.Read )
		l = IECore.LinkedScene( m )
		# test Write mode
		m = IECore.LinkedScene( "/tmp/test.lscc", IECore.IndexedIO.OpenMode.Write )
		self.assertTrue( isinstance( m, IECore.LinkedScene ) )
		self.assertEqual( m.fileName(), "/tmp/test.lscc" )
		self.assertRaises( RuntimeError, m.readBound, 0.0 )
		del m
		# test Read mode
		m = IECore.LinkedScene( "/tmp/test.lscc", IECore.IndexedIO.OpenMode.Read )
		self.assertTrue( isinstance( m, IECore.LinkedScene ) )
		self.assertEqual( m.fileName(), "/tmp/test.lscc" )
		m.readBound( 0.0 )

	def testAppendRaises( self ) :
		self.assertRaises( RuntimeError, IECore.SceneInterface.create, "/tmp/test.lscc", IECore.IndexedIO.OpenMode.Append )
		self.assertRaises( RuntimeError, IECore.LinkedScene, "/tmp/test.lscc", IECore.IndexedIO.OpenMode.Append )

	def testReadNonExistentRaises( self ) :
		self.assertRaises( RuntimeError, IECore.LinkedScene, "iDontExist.lscc", IECore.IndexedIO.OpenMode.Read )

	def testLinkAttribute( self ):

		self.assertEqual( IECore.LinkedScene.linkAttribute, "sceneInterface:link" )

		m = IECore.SceneCache( "test/IECore/data/sccFiles/animatedSpheres.scc", IECore.IndexedIO.OpenMode.Read )
		attr = IECore.LinkedScene.linkAttributeData( m )
		expectedAttr = IECore.CompoundData( 
			{
				"fileName": IECore.StringData("test/IECore/data/sccFiles/animatedSpheres.scc"), 
				"root": IECore.InternedStringVectorData( [] )
			}
		)
		self.assertEqual( attr, expectedAttr )

		A = m.child("A")
		attr = IECore.LinkedScene.linkAttributeData( A )
		expectedAttr = IECore.CompoundData( 
			{
				"fileName": IECore.StringData("test/IECore/data/sccFiles/animatedSpheres.scc"), 
				"root": IECore.InternedStringVectorData( [ 'A' ] )
			}
		)
		self.assertEqual( attr, expectedAttr )

		A = m.child("A")
		attr = IECore.LinkedScene.linkAttributeData( A, 10.0 )
		expectedAttr['time'] = IECore.DoubleData(10.0)
		self.assertEqual( attr, expectedAttr )
		
	def testWriting( self ):

		m = IECore.SceneCache( "test/IECore/data/sccFiles/animatedSpheres.scc", IECore.IndexedIO.OpenMode.Read )
		A = m.child("A")

		l = IECore.LinkedScene( "/tmp/test.lscc", IECore.IndexedIO.OpenMode.Write )
		i0 = l.createChild("instance0")
		i0.writeLink( m )
		i1 = l.createChild("instance1")
		i1.writeLink( m )
		i1.writeAttribute( "testAttr", IECore.StringData("test"), 0 )
		i1.writeTransform( IECore.M44dData( IECore.M44d.createTranslated( IECore.V3d( 1, 0, 0 ) ) ), 0.0 )
		i2 = l.createChild("instance2")
		i2.writeLink( A )
		i2.writeTransform( IECore.M44dData( IECore.M44d.createTranslated( IECore.V3d( 2, 0, 0 ) ) ), 0.0 )
		self.assertRaises( RuntimeError, i2.createChild, "cannotHaveChildrenAtLinks" )
		self.assertRaises( RuntimeError, i2.writeTags, ["cannotHaveTagsAtLinks"] )
		self.assertRaises( RuntimeError, i2.writeObject, IECore.SpherePrimitive( 1 ), 0.0 )  # cannot save objects at link locations.
		b1 = l.createChild("branch1")
		b1.writeObject( IECore.SpherePrimitive( 1 ), 0.0 )
		self.assertRaises( RuntimeError, b1.writeLink, A )
		b2 = l.createChild("branch2")
		c2 = b2.createChild("child2")
		self.assertRaises( RuntimeError, b2.writeLink, A )
		del i0, i1, i2, l, b1, b2, c2

		l = IECore.LinkedScene( "/tmp/test.lscc", IECore.IndexedIO.OpenMode.Read )

		self.assertEqual( l.numBoundSamples(), 4 )
		self.assertEqual( set(l.childNames()), set(['instance0','instance1','instance2','branch1','branch2']) )
		i0 = l.child("instance0")
		self.assertEqual( i0.numBoundSamples(), 4 )
		self.failUnless( LinkedSceneTest.compareBBox( i0.readBoundAtSample(0), IECore.Box3d( IECore.V3d( -1,-1,-1 ), IECore.V3d( 2,2,1 ) ) ) )
		self.failUnless( LinkedSceneTest.compareBBox( i0.readBoundAtSample(1), IECore.Box3d( IECore.V3d( -1,-1,-1 ), IECore.V3d( 3,3,1 ) ) ) )
		self.failUnless( LinkedSceneTest.compareBBox( i0.readBoundAtSample(2), IECore.Box3d( IECore.V3d( -2,-1,-2 ), IECore.V3d( 4,5,2 ) ) ) )
		self.failUnless( LinkedSceneTest.compareBBox( i0.readBoundAtSample(3), IECore.Box3d( IECore.V3d( -3,-1,-3 ), IECore.V3d( 4,6,3 ) ) ) )
		self.failUnless( LinkedSceneTest.compareBBox( i0.readBound(0), IECore.Box3d( IECore.V3d( -1,-1,-1 ), IECore.V3d( 2,2,1 ) ) ) )

		A = i0.child("A")
		self.failUnless( LinkedSceneTest.compareBBox( A.readBoundAtSample(0), IECore.Box3d(IECore.V3d( -1,-1,-1 ), IECore.V3d( 1,1,1 ) ) ) )
		self.failUnless( LinkedSceneTest.compareBBox( A.readBoundAtSample(1), IECore.Box3d(IECore.V3d( -1,-1,-1 ), IECore.V3d( 1,1,1 ) ) ) )
		self.failUnless( LinkedSceneTest.compareBBox( A.readBoundAtSample(2), IECore.Box3d(IECore.V3d( 0,-1,-1 ), IECore.V3d( 2,1,1 ) ) ) )
		self.assertEqual( i0.readTransform( 0 ), IECore.M44dData( IECore.M44d() ) )

		i1 = l.child("instance1")
		self.assertEqual( i1.numBoundSamples(), 4 )
		self.failUnless( LinkedSceneTest.compareBBox( i1.readBoundAtSample(0), IECore.Box3d( IECore.V3d( -1,-1,-1 ), IECore.V3d( 2,2,1 ) ) ) )
		self.failUnless( LinkedSceneTest.compareBBox( i1.readBoundAtSample(2), IECore.Box3d( IECore.V3d( -2,-1,-2 ), IECore.V3d( 4,5,2 ) ) ) )
		self.failUnless( LinkedSceneTest.compareBBox( i1.readBoundAtSample(3), IECore.Box3d( IECore.V3d( -3,-1,-3 ), IECore.V3d( 4,6,3 ) ) ) )
		self.failUnless( LinkedSceneTest.compareBBox( i1.readBound(0), IECore.Box3d( IECore.V3d( -1,-1,-1 ), IECore.V3d( 2,2,1 ) ) ) )
		self.assertEqual( i1.readTransform( 0 ), IECore.M44dData( IECore.M44d.createTranslated( IECore.V3d( 1, 0, 0 ) ) ) )
		self.assertEqual( i1.readAttribute( "testAttr", 0 ), IECore.StringData("test") )
		
		i2 = l.child("instance2")
		self.assertEqual( i2.numBoundSamples(), 3 )
		self.failUnless( LinkedSceneTest.compareBBox( i2.readBoundAtSample(0), IECore.Box3d(IECore.V3d( -1,-1,-1 ), IECore.V3d( 1,1,1 ) ) ) )
		self.failUnless( LinkedSceneTest.compareBBox( i2.readBoundAtSample(1), IECore.Box3d(IECore.V3d( -1,-1,-1 ), IECore.V3d( 1,1,1 ) ) ) )
		self.failUnless( LinkedSceneTest.compareBBox( i2.readBoundAtSample(2), IECore.Box3d(IECore.V3d( 0,-1,-1 ), IECore.V3d( 2,1,1 ) ) ) )
		self.assertEqual( i2.readTransform( 0 ), IECore.M44dData( IECore.M44d.createTranslated( IECore.V3d( 2, 0, 0 ) ) ) )

		self.assertEqual( l.scene( [ 'instance0' ] ).path(), [ 'instance0' ] )
		self.assertEqual( l.scene( [ 'instance0', 'A' ] ).path(), [ 'instance0', 'A' ] )
		self.assertEqual( i0.path(), [ 'instance0' ] )

		# test saving a two level LinkedScene
		l2 = IECore.LinkedScene( "/tmp/test2.lscc", IECore.IndexedIO.OpenMode.Write )
		base = l2.createChild("base")
		t1 = base.createChild("test1")
		t1.writeLink( l )
		t2 = base.createChild("test2")
		t2.writeLink( i0 )
		t3 = base.createChild("test3")
		t3.writeLink( i1 )
		t4 = base.createChild("test4")
		t4.writeLink( i2 )
		t5 = base.createChild("test5")
		t5.writeLink( A )
		del l2, t1, t2, t3, t4, t5

	def testTimeRemapping( self ):

		m = IECore.SceneCache( "test/IECore/data/sccFiles/animatedSpheres.scc", IECore.IndexedIO.OpenMode.Read )

		l = IECore.LinkedScene( "/tmp/test.lscc", IECore.IndexedIO.OpenMode.Write )
		# save animated spheres with double the speed and with offset, using less samples (time remapping)
		i0 = l.createChild("instance0")
		i0.writeAttribute( IECore.LinkedScene.linkAttribute, IECore.LinkedScene.linkAttributeData( m, 0.0 ), 1.0 )
		i0.writeAttribute( IECore.LinkedScene.linkAttribute, IECore.LinkedScene.linkAttributeData( m, 3.0 ), 2.0 )
		# save animated spheres with same speed and with offset, same samples (time remapping is identity)
		i1 = l.createChild("instance1")
		i1.writeAttribute( IECore.LinkedScene.linkAttribute, IECore.LinkedScene.linkAttributeData( m, 0.0 ), 1.0 )
		i1.writeAttribute( IECore.LinkedScene.linkAttribute, IECore.LinkedScene.linkAttributeData( m, 1.0 ), 2.0 )
		i1.writeAttribute( IECore.LinkedScene.linkAttribute, IECore.LinkedScene.linkAttributeData( m, 2.0 ), 3.0 )
		i1.writeAttribute( IECore.LinkedScene.linkAttribute, IECore.LinkedScene.linkAttributeData( m, 3.0 ), 4.0 )
		# save animated spheres with half the speed, adding more samples to a range of the original (time remapping)
		i2 = l.createChild("instance2")
		i2.writeAttribute( IECore.LinkedScene.linkAttribute, IECore.LinkedScene.linkAttributeData( m, 0.0 ), 0.0 )
		i2.writeAttribute( IECore.LinkedScene.linkAttribute, IECore.LinkedScene.linkAttributeData( m, 0.5 ), 1.0 )
		i2.writeAttribute( IECore.LinkedScene.linkAttribute, IECore.LinkedScene.linkAttributeData( m, 1.0 ), 2.0 )

		del i0, i1, i2, l

		l = IECore.LinkedScene( "/tmp/test.lscc", IECore.IndexedIO.OpenMode.Read )
		self.assertEqual( l.numBoundSamples(), 5 )
		i0 = l.child("instance0")
		self.assertEqual( i0.numBoundSamples(), 2 )
		self.assertEqual( i0.numTransformSamples(), 1 )
		self.assertEqual( i0.readTransformAtSample(0), IECore.M44dData() )
		A0 = i0.child("A")
		self.assertEqual( A0.numBoundSamples(), 2 )
		self.assertEqual( A0.numTransformSamples(), 2 )
		self.failUnless( LinkedSceneTest.compareBBox( A0.readBoundAtSample(0), IECore.Box3d(IECore.V3d( -1,-1,-1 ), IECore.V3d( 1,1,1 ) ) ) )
		self.failUnless( LinkedSceneTest.compareBBox( A0.readBoundAtSample(1), IECore.Box3d(IECore.V3d( 0,-1,-1 ), IECore.V3d( 2,1,1 ) ) ) )
		self.assertEqual( A0.readTransformAtSample(0), IECore.M44dData( IECore.M44d.createTranslated( IECore.V3d( 1, 0, 0 ) ) ) )
		self.assertEqual( A0.readTransformAtSample(1), IECore.M44dData( IECore.M44d.createTranslated( IECore.V3d( 2, 0, 0 ) ) ) )
		i1 = l.child("instance1")
		self.assertEqual( i1.numBoundSamples(), 4 )
		self.assertEqual( i1.numTransformSamples(), 1 )
		A1 = i1.child("A")
		self.assertEqual( A1.numTransformSamples(), 4 )
		self.assertEqual( A1.readTransformAtSample(0), IECore.M44dData( IECore.M44d.createTranslated( IECore.V3d( 1, 0, 0 ) ) ) )
		self.assertEqual( A1.readTransformAtSample(1), IECore.M44dData( IECore.M44d.createTranslated( IECore.V3d( 2, 0, 0 ) ) ) )
		self.assertEqual( A1.readTransformAtSample(2), IECore.M44dData( IECore.M44d.createTranslated( IECore.V3d( 2, 0, 0 ) ) ) )
		self.assertEqual( A1.readTransformAtSample(3), IECore.M44dData( IECore.M44d.createTranslated( IECore.V3d( 2, 0, 0 ) ) ) )
		i2 = l.child("instance2")
		self.assertEqual( i2.numBoundSamples(), 3 )
		self.assertEqual( i2.numTransformSamples(), 1 )
		A2 = i2.child("A")
		self.assertEqual( A2.numBoundSamples(), 3 )
		self.assertEqual( A2.numTransformSamples(), 3 )
		self.assertEqual( A2.readTransform(1.0), IECore.M44dData( IECore.M44d.createTranslated( IECore.V3d( 1.5, 0, 0 ) ) ) )
		self.assertEqual( A2.readTransformAtSample(0), IECore.M44dData( IECore.M44d.createTranslated( IECore.V3d( 1, 0, 0 ) ) ) )
		self.assertEqual( A2.readTransformAtSample(1), IECore.M44dData( IECore.M44d.createTranslated( IECore.V3d( 1.5, 0, 0 ) ) ) )
		self.assertEqual( A2.readTransformAtSample(2), IECore.M44dData( IECore.M44d.createTranslated( IECore.V3d( 2, 0, 0 ) ) ) )
		

	def testReading( self ):

		def recurseCompare( basePath, virtualScene, realScene, atLink = True ) :
			self.assertEqual( basePath, virtualScene.path() )

			if not atLink :	# attributes and tranforms at link location are not loaded.

				self.assertEqual( set(virtualScene.attributeNames()), set(realScene.attributeNames()) )
				for attr in realScene.attributeNames() :
					self.assertTrue( virtualScene.hasAttribute( attr ) )
					self.assertEqual( virtualScene.numAttributeSamples(attr), realScene.numAttributeSamples(attr) )
					for s in xrange(0,virtualScene.numAttributeSamples(attr)) :
						self.assertEqual( virtualScene.readAttributeAtSample(attr, s), realScene.readAttributeAtSample(attr, s) )

				self.assertEqual( virtualScene.numTransformSamples(), realScene.numTransformSamples() )
				for s in xrange(0,virtualScene.numTransformSamples()) :
					self.assertEqual( virtualScene.readTransformAtSample(s), realScene.readTransformAtSample(s) )

			self.assertEqual( virtualScene.numBoundSamples(), realScene.numBoundSamples() )
			for s in xrange(0,virtualScene.numBoundSamples()) :
				self.assertEqual( virtualScene.readBoundAtSample(s), realScene.readBoundAtSample(s) )

			self.assertEqual( virtualScene.hasObject(), realScene.hasObject() )
			if virtualScene.hasObject() :
				self.assertEqual( virtualScene.numObjectSamples(), realScene.numObjectSamples() )
				for s in xrange(0,virtualScene.numObjectSamples()) :
					self.assertEqual( virtualScene.readObjectAtSample(s), realScene.readObjectAtSample(s) )

			self.assertEqual( set(virtualScene.childNames()), set(realScene.childNames()) )
			for c in virtualScene.childNames() :
				self.assertTrue( virtualScene.hasChild(c) )
				recurseCompare( basePath + [ str(c) ], virtualScene.child(c), realScene.child(c), False )

		env = IECore.LinkedScene( "test/IECore/data/sccFiles/environment.lscc", IECore.IndexedIO.OpenMode.Read )
		l = IECore.LinkedScene( "test/IECore/data/sccFiles/instancedSpheres.lscc", IECore.IndexedIO.OpenMode.Read )
		m = IECore.SceneCache( "test/IECore/data/sccFiles/animatedSpheres.scc", IECore.IndexedIO.OpenMode.Read )

		base = env.child('base')
		self.assertEqual( set(base.childNames()), set(['test1','test2','test3','test4','test5']) )
		test1 = base.child('test1')
		self.assertEqual( test1.path(), [ "base", "test1" ] )
		recurseCompare( test1.path(), test1, l )
		test2 = base.child('test2')
		self.assertEqual( test2.path(), [ "base", "test2" ] )
		recurseCompare( test2.path(), test2, l.child('instance0') )
		test3 = base.child('test3')
		self.assertEqual( test3.path(), [ "base", "test3" ] )
		recurseCompare( test3.path(), test3, l.child('instance1') )
		test4 = base.child('test4')
		self.assertEqual( test4.path(), [ "base", "test4" ] )
		recurseCompare( test4.path(), test4, l.child('instance2') )
		test5 = base.child('test5')
		self.assertEqual( test5.path(), [ "base", "test5" ] )
		recurseCompare( test5.path(), test5, l.child('instance1').child('A') )
		
		self.assertEqual( test1.child('instance0').path(), [ "base", "test1", "instance0" ] )
		recurseCompare( test1.child('instance0').path(), test1.child('instance0'), m )
		recurseCompare( test2.path(), test2, m )
		recurseCompare( test3.path(), test3, m )
		recurseCompare( test4.path(), test4, m.child('A') )
		recurseCompare( test5.path(), test5, m.child('A') )

		recurseCompare( test1.path(), env.scene( [ 'base', 'test1' ] ), l )
		recurseCompare( test1.path(), env.scene( [ 'base' ] ).child( 'test1' ), l )

	def testTags( self ) :

		def testSet( values ):
			return set( map( lambda s: IECore.InternedString(s), values ) )

		# create a base scene
		l = IECore.LinkedScene( "/tmp/test.lscc", IECore.IndexedIO.OpenMode.Write )
		a = l.createChild('a')
		a.writeTags( [ "test" ] )
		l.writeTags( [ "tags" ] )
		del a, l

		# now create a linked scene that should inherit the tags from the base one, plus add other ones
		l = IECore.LinkedScene( "/tmp/test.lscc", IECore.IndexedIO.OpenMode.Read )
		a = l.child('a')

		self.assertEqual( set(l.readTags()), testSet(["test","tags"]) )
		self.assertEqual( set(l.readTags(includeChildren=False)), testSet(["tags"]) )
		self.assertEqual( set(a.readTags()), testSet(["test"]) )
		self.assertEqual( set(a.readTags(includeChildren=False)), testSet(["test"]) )

		l2 = IECore.LinkedScene( "/tmp/test2.lscc", IECore.IndexedIO.OpenMode.Write )

		A = l2.createChild('A')
		A.writeLink( l )
		self.assertRaises( RuntimeError, A.writeTags, ['cantCreateAtLinks'] )

		B = l2.createChild('B')
		B.writeLink( a )

		C = l2.createChild('C')
		c = C.createChild('c')
		c.writeLink( l )
		C.writeTags( [ 'C' ] )

		D = l2.createChild('D')
		D.writeTags( [ 'D' ] )
		self.assertRaises( RuntimeError, D.writeLink, a )	# should not allow creating links to scene locations that have tags assigned.

		del l, a, l2, A, B, C, c, D

		l2 = IECore.LinkedScene( "/tmp/test2.lscc", IECore.IndexedIO.OpenMode.Read )
		A = l2.child("A")
		Aa = A.child("a")
		B = l2.child("B")
		C = l2.child("C")
		c = C.child("c")
		ca = c.child("a")
		D = l2.child("D")

		self.assertEqual( set(l2.readTags()), testSet(["test","tags","C", "D"]) )
		self.assertEqual( set(l2.readTags(includeChildren=False)), testSet([]) )
		self.assertEqual( set(A.readTags()), testSet(["test","tags"]) )
		self.assertEqual( set(A.readTags(includeChildren=False)), testSet(["tags"]) )
		self.assertEqual( set(Aa.readTags()), testSet(["test"]) )
		self.assertEqual( set(Aa.readTags(includeChildren=False)), testSet(["test"]) )
		self.assertEqual( set(B.readTags()), testSet(["test"]) )
		self.assertEqual( set(C.readTags()), testSet(["test","tags","C"]) )
		self.assertEqual( set(C.readTags(includeChildren=False)), testSet(["C"]) )
		self.assertEqual( set(c.readTags()), testSet(["test","tags"]) )
		self.assertEqual( set(c.readTags(includeChildren=False)), testSet(["tags"]) )
		self.assertEqual( set(ca.readTags()), testSet(["test"]) )
		self.assertEqual( set(C.readTags(includeChildren=False)), testSet(["C"]) )
		self.assertEqual( set(D.readTags()), testSet(["D"]) )

if __name__ == "__main__":
	unittest.main()

