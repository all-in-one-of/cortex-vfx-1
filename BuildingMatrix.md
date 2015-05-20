The cortex wiki is now hosted at https://github.com/ImageEngine/cortex/wiki
#summary Build Matrix for Cortex 5

# Introduction #

There is no standard library configuration that software developers are using. So different kind of standard software like Maya or Houdini might need a different library configuration. In a studio environment you might want to work with Cortex across multiple software platforms and hence you will have to build a specific Cortex configuration that works with the intended 3rd party software.
The below build matrix shows a number of configuration that are successfully being used in a Linux environment and Cortex 5.

# Build Matrix #

The 'odd ones out' are in **bold**.

| Configuration Name / Library | **Base** | **Maya2010** | **Maya2011** | **Maya2012** | **Houdini11.0** | **Houdini12.0** | **Houdini12.1** | **Nuke6.0v3** | **Nuke6.3v7** | **Arnold 4.0.8.0** |
|:-----------------------------|:---------|:-------------|:-------------|:-------------|:----------------|:----------------|:----------------|:--------------|:--------------|:-------------------|
| **gcc**                      | 4.1.2    | 4.1.2        | 4.1.2        | 4.1.2        | 4.1.2           | 4.1.2           | 4.1.2           | **3.4.6**     | 4.1.2         | 4.1.2              |
| **Python**                   | 2.6      | 2.6          | 2.6          | 2.6          | **2.5**         | 2.6             | 2.6             | **2.5**       | 2.6           | 2.6                |
| **Boost**                    | 1.46.1   | 1.42.0       | 1.42.0       | 1.46.1       | **1.37.0**      | 1.46.1          | 1.46.1          | **1.38.0**    | 1.46.1        | **1.43**           |
| **TBB**                      | 2.2      | 2.2          | 2.2          | 2.2          | 2.2             | 2.2`*`          | 2.2`*`          | 2.2           | 2.2           | 2.2                |
| **IlmBase**                  | 1.0.1    | 1.0.1        | 1.0.1        | 1.0.1        | 1.0.1           | 1.0.1           | 1.0.1           | 1.0.1         | 1.0.1         | 1.0.1              |
| **OpenEXR**                  | 1.6.1    | 1.6.1        | 1.6.1        | 1.6.1        | 1.6.1           | **1.7.0**       | **1.7.0**       |1.6.1          | 1.6.1         | 1.6.1              |
| **Freetype**                 | 2.3.7    |2.3.5         | 2.3.7        | 2.3.5        | 2.3.7           | 2.3.7           | 2.3.7           | 2.3.5         | 2.3.5         | 2.3.5              |
| **GLEW**                     | 1.5.3    | 1.4.0        | 1.5.3        | 1.4.0        | 1.5.3           | 1.5.3           | 1.5.3           | 1.4.0         | 1.4.0         | 1.4.0              |
| **Freeglut**                 | 2.6.0    |              | 2.6.0        |              | 2.6.0           | 2.6.0           | 2.6.0           |               |               |                    |
| **Doxygen**                  | 1.5.7    | 1.5.8        | 1.5.7        | 1.7.3        | 1.5.7           | 1.7.3           | 1.7.3           | 1.5.8         | 1.7.3         | 1.7.3              |
| **3delight**                 |          | 9.0.44       | 9.0.36       | 10.0.62      | 9.0.36          | 10.0.62         | 10.0.62         |  9.0.31       | 10.0.62       |                    |
| **Maya**                     |          | 2010         | 2011         | 2012         |                 |                 |                 |               |               | 2012               |
| **Houdini**                  |          |              |              |              | 11              | 12              | 12              |               |               |                    |
| **Nuke**                     |          |              |              |              |                 |                 |                 | 6.0v3         | 6.3v7         |                    |
|                              |          |              |              |              |                 |                 |                 |               |               |                    |
| **_Status_**                 | ok       | ok           | untested     | ok           | ok              | ok              | ok              | ok            | ok            | ok                 |
| **_last checked with Cortex_** | 7.7.2    | 5.5.0        |              | 7.7.2        | 6.4.3           | 7.7.2           | 7.7.2           | 5.5.0         | 7.7.2         | 7.6.0              |

Notes:
  * Maya and Houdini use different TBB  versions than 2.2, but all claim compatibility - so far no adverse affects have been noticed using Cortex linked against TBB 2.2 with and Maya or Houdini Version
  * Cortex 7 only works with Houdini 12.0 and higher. It is incompatible with Houdini 11 and previous
  * Arnold requires Boost 1.43