package com.jiaoew.recommander

import io.prediction.controller.IEngineFactory
import io.prediction.controller.Engine

case class Query(userId: String, likes: List[String], start: Int, size: Int, profiles: Option[Set[Double]],
  blackList: Option[Set[String]]) extends Serializable

case class PredictedResult(itemScores: Array[ItemScore]) extends Serializable

case class ItemScore(item: String, score: Double) extends Serializable

object SimilarityEngine extends IEngineFactory {
  def apply() = {
    new Engine(
      classOf[DataSource],
      classOf[Preparator],
      Map("als" -> classOf[ALSAlgorithm]),
      classOf[Serving])
  }
}
