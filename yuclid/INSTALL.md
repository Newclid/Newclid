# Installation

## Binary download

The simplest way to install Yuclid is to get a prebuilt static binary,
either from Github releases webpage,
or by installing `pip install newclid[yuclid]`.

If you want to install Yuclid without installing Newclid,
then you may run `pip install --no-deps yuclid` instead.

## Building from source

In order to build Yuclid from source, you need:

- [CMake](https://cmake.org/) build system;
- [Boost libraries](https://boost.org/), at least version 1.83;
- A recent C++ compiler. These versions are known to work:
  - [g++-14](https://gcc.gnu.org/)
  - [clang++-19](http://clang.llvm.org/)
  - [Visual Studio 17 2022](https://visualstudio.microsoft.com/vs/features/cplusplus/)

The build follows the usual `cmake` routine:

```shell
$ mkdir build
$ cd build
$ cmake -DCMAKE_BUILD_TYPE=RelWithDebInfo -DCMAKE_INSTALL_PREFIX=/some/prefix ..
$ cmake --build .
$ cmake --install .
```

If you have a recent compiler on your system,
but it is not the default one, you may want to pass, e.g., `-DCMAKE_CXX_COMPILER=g++-14`
to the `cmake ..` command.
