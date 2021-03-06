![Build status](https://travis-ci.org/davidkleiven/CEMC.svg?branch=master)
[![MIT License](https://img.shields.io/github/license/mashape/apistatus.svg?maxAge=2592000)](LICENSE)
[![No Maintenance Intended](http://unmaintained.tech/badge.svg)](http://unmaintained.tech/)
# Cluster Expansion Monte Carlo

Please consult the [official CLEASE repository](https://gitlab.com/computationalmaterials/clease) instead.

[Documentation page](http://folk.ntnu.no/davidkl/CEMC/index.html)

# Dependencies
* ~~[SWIG](http://www.swig.org/) (newer than version 3.0)~~ (not anymore!)
* [GCC](https://gcc.gnu.org/) (has to support multithreading)
* Python packages listed in [requirements.txt](requirements.txt)

# Installation
Install all the dependencies on Ubuntu
```bash
sudo apt-get update
sudo apt-get install g++
```

Install the python dependencies (at the moment this only works for Python 2)
```bash
pip install -r requirements.txt
```

Install the package
```bash
pip install .
```

Run the all tests
```bash
python tests/runner.py
```

# Examples
Examples of application of the package are listed below

* [Ground State of Al-Mg](examples/ex_ground_state.py)
* [Monte Carlo in SGC Ensemble](examples/ex_sgc_montecarlo.py)
* [Computing Free Energy From MC data](examples/ex_free_energy_calculations.py)
* [Free Energies in the SGC ensemble](examples/ex_free_energy_sgc.py)
* [Using MC observers to extract information on each MC step](examples/ex_using_mc_observers.py)

# Troubleshooting
1. **Missing C++ version of CE updater** try to install with
```bash
pip install -e .
```
instead.

2. **Compilation fails**
During development of this package it has mainly been compiled with GCC,
so if compilation fail it can be worth testing
```bash
env CC=gcc CXX=g++ pip install -e .
```
note that a GCC version supporting openMP is required.

3. **Installing with Intel Compilers**
If installing with Intel compilers prepending some paths before the pip command 
might help
```bash
CC=icc LINKCC=icc LDSHARED="icc -shared" pip install .
```

# Guidelines
Any code that is in this repository should have *at least* one unittest
located in the *tests* folder. The minimum test required is that the
code does what it is supposed to do without raising unexpected exceptions.
Code producing results that can be verified against some reference values,
should also include tests verifying that the code produce the desired result.

At any time *ALL* tests in the *tests* folder should pass, meaning that
```bash
python tests/runner.py
```
should give no errors.
