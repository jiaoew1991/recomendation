

assemblySettings

name := "recommender"

organization := "com.jiaoew"

libraryDependencies ++= Seq(
  "io.prediction" %% "core" % "0.8.5" % "provided",
  "org.apache.spark" %% "spark-core" % "1.2.0" % "provided",
  "org.apache.spark" %% "spark-mllib" % "1.2.0" % "provided")
