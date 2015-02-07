

assemblySettings

name := "template-scala-parallel-similar"

organization := "io.prediction"

libraryDependencies ++= Seq(
  "io.prediction" %% "core" % "0.8.5" % "provided",
  "io.spray" %% "spray-can" % "1.3.2" % "provided",
  "io.spray" %% "spray-routing" % "1.3.2" % "provided",
  "org.apache.spark" %% "spark-core" % "1.2.0" % "provided",
  "org.apache.spark" %% "spark-mllib" % "1.2.0" % "provided")
