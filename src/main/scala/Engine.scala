import io.prediction.controller.IEngineFactory
import io.prediction.controller.Engine

case class Query(userId: String, items: List[String], num: Int, profiles: Option[Set[String]],
  whiteList: Option[Set[String]], blackList: Option[Set[String]]) extends Serializable

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
