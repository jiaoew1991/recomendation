import grizzled.slf4j.Logger
import io.prediction.controller.{EmptyActualResult, EmptyEvaluationInfo, PDataSource, Params}
import io.prediction.data.storage.Storage
import org.apache.spark.SparkContext
import org.apache.spark.rdd.RDD

case class DataSourceParams(appId: Int, like: Double, dislike: Double) extends Params

class DataSource(val dsp: DataSourceParams) extends PDataSource[TrainingData, EmptyEvaluationInfo, Query, EmptyActualResult] {

  @transient lazy val logger = Logger[this.type]

  override def readTraining(sc: SparkContext): TrainingData = {
    val eventsDb = Storage.getPEvents()

    // create a RDD of (entityID, User)
    val usersRDD: RDD[(String, User)] = eventsDb.aggregateProperties(
      appId = dsp.appId,
      entityType = "user"
    )(sc).map { case (entityId, properties) =>
      val user = try {
        User(profiles = properties.getOpt[List[String]]("profiles"))
      } catch {
        case e: Exception => {
          logger.error(s"Failed to get properties ${properties} of" +
            s" user ${entityId}. Exception: ${e}.")
          throw e
        }
      }
      (entityId, user)
    }

    // create a RDD of (entityID, Item)
    val itemsRDD: RDD[(String, Item)] = eventsDb.aggregateProperties(
      appId = dsp.appId,
      entityType = "item"
    )(sc).map { case (entityId, properties) =>
      val item = try {
        // Assume categories is optional property of item.
        Item(profiles = properties.getOpt[List[String]]("profiles"))
      } catch {
        case e: Exception => {
          logger.error(s"Failed to get properties ${properties} of" +
            s" item ${entityId}. Exception: ${e}.")
          throw e
        }
      }
      (entityId, item)
    }

    // get all "user" "like" "item" events
    val viewEventsRDD: RDD[LikeEvent] = eventsDb.find(
      appId = dsp.appId,
      entityType = Some("user"),
      eventNames = Some(List("like", "dislike")),
      targetEntityType = Some(Some("item")))(sc).map { event =>
      val viewEvent = try {
        event.event match {
          case "like" => LikeEvent(event.entityId, event.targetEntityId.get, dsp.like, event.eventTime.getMillis)
          case "dislike" => LikeEvent(event.entityId, event.targetEntityId.get, dsp.dislike, event.eventTime.getMillis)
          case _ => throw new Exception(s"Unexpected event ${event} is read.")
        }
      } catch {
        case e: Exception => {
          logger.error(s"Cannot convert ${event} to ViewEvent." +
            s" Exception: ${e}.")
          throw e
        }
      }
      viewEvent
    }

    new TrainingData(
      users = usersRDD,
      items = itemsRDD,
      viewEvents = viewEventsRDD
    )
  }
}

case class User(profiles: Option[List[String]])

case class Item(profiles: Option[List[String]])

case class LikeEvent(user: String, item: String, score: Double, t: Long)

class TrainingData(
                    val users: RDD[(String, User)],
                    val items: RDD[(String, Item)],
                    val viewEvents: RDD[LikeEvent]
                    ) extends Serializable {
  override def toString = {
    s"users: [${users.count()} (${users.take(2).toList}...)]" +
      s"items: [${items.count()} (${items.take(2).toList}...)]" +
      s"viewEvents: [${viewEvents.count()}] (${viewEvents.take(2).toList}...)"
  }
}
