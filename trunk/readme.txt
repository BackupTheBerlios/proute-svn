* How to load my data?
  First, try using the generic input plugins, by formatting your data for it.
  If the generic plugins are not generic enough for your data, then suport must
  be added for it, either by asking the developer and hoping he has time or by
  adding support yourself.

* How to add support for a new problem type, or for a new instance type:
  Derive the class vrpdata.VrpInputData:
  - define the defaultFor and instanceType class attributes
  - define the loadData(fName) method
  The plugins directory has several examples of how to do that.

* How to add support for a new solution type:
  Derive the class vrpdata.VrpSolutionData:
  - define the defaultFor and solutionType class attributes
  - define the loadData(fName) method
  The plugins directory is rich with examples, from simple ones (cvrp)
  to more complex ones (mcdarp).

* How to add a new visual effect:
  Derive the class style.Style:
  - define the description, parameterInfo and parameterValue class attributes
  - define the paint() method
  Examples can be found in the plugins directory, see e.g. module basestyles;
  (a bit) more documentation can be found in class style.Style.
