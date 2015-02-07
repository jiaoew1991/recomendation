package com.jiaoew.recommander

import grizzled.slf4j.Logger
import io.prediction.controller.{PAlgorithm, Params}
import io.prediction.data.storage.BiMap
import org.apache.spark.SparkContext._
import org.apache.spark.mllib.recommendation.{ALS, ALSModel, Rating => MLlibRating}
import org.jblas.DoubleMatrix

import scala.collection.mutable.PriorityQueue

case class ALSAlgorithmParams(rank: Int, numIterations: Int, similarSize: Int) extends Params

/**
 * Use ALS to build item x feature matrix
 */
class ALSAlgorithm(val ap: ALSAlgorithmParams) extends PAlgorithm[PreparedData, ALSModel, Query, PredictedResult] {

  @transient lazy val logger = Logger[this.type]

  def train(data: PreparedData): ALSModel = {
    require(!data.viewEvents.take(1).isEmpty,
      s"viewEvents in PreparedData cannot be empty." +
        " Please check if DataSource generates TrainingData" +
        " and Preprator generates PreparedData correctly.")
    require(!data.users.take(1).isEmpty,
      s"users in PreparedData cannot be empty." +
        " Please check if DataSource generates TrainingData" +
        " and Preprator generates PreparedData correctly.")
    require(!data.items.take(1).isEmpty,
      s"items in PreparedData cannot be empty." +
        " Please check if DataSource generates TrainingData" +
        " and Preprator generates PreparedData correctly.")
    // create User and item's String ID to integer index BiMap
    val userStringIntMap = BiMap.stringInt(data.users.keys)
    val itemStringIntMap = BiMap.stringInt(data.items.keys)

    // collect Item as Map and convert ID to Int index
    val items: Map[Int, Item] = data.items.map { case (id, item) =>
      (itemStringIntMap(id), item)
    }.collectAsMap.toMap

    val itemCount = items.size
    val sc = data.viewEvents.context
    val mllibRatings = data.viewEvents.map { r =>
      // Convert user and item String IDs to Int index for MLlib
      val uindex = userStringIntMap.getOrElse(r.user, -1)
      val iindex = itemStringIntMap.getOrElse(r.item, -1)

      if (uindex == -1)
        logger.info(s"Couldn't convert nonexistent user ID ${r.user}"
          + " to Int index.")

      if (iindex == -1)
        logger.info(s"Couldn't convert nonexistent item ID ${r.item}"
          + " to Int index.")

      ((uindex, iindex), r.score)
    }.filter { case ((u, i), v) =>
      // keep events with valid user and item index
      (u != -1) && (i != -1)
    }.reduceByKey(_ + _) // aggregate all view events of same user-item pair
      .map { case ((u, i), v) =>
      // MLlibRating requires integer index for user and item
      MLlibRating(u, i, v)
    }

    // MLLib ALS cannot handle empty training data.
    require(!mllibRatings.take(1).isEmpty,
      s"mllibRatings cannot be empty." +
        " Please check if your events contain valid user and item ID.")
    val m = ALS.trainImplicit(mllibRatings, ap.rank, ap.numIterations)

    new ALSModel(m.rank, m.userFeatures, m.productFeatures, itemStringIntMap, items)
  }

  def predict(model: ALSModel, query: Query): PredictedResult = {

    val blackList: Option[Set[Int]] = query.blackList.map(set =>
      set.map(model.itemStringIntMap.get(_)).flatten
    )

    val toFeatures = model.itemStringIntMap.get(query.userId).map { userInt =>
      model.userFeatures.lookup(userInt).head
    } getOrElse {
      // or find similar user's recommendation
      val similar = similarUser(model.items, query.profiles.getOrElse(Set.empty[Double])).
        map(pair => model.userFeatures.lookup(pair._1).head).
        reduce(_.zip(_).map(p => p._1 + p._2)).map(_ / ap.similarSize)
      logger.debug(s"similar features is $similar")
      similar
    }

    val recommendVector = new DoubleMatrix(toFeatures)
    val scored = model.productFeatures.map { case (id, features) =>
      (id, recommendVector.dot(new DoubleMatrix(features)))
    }

    implicit val ord = Ordering.by[(Int, Double), Double](_._2)

    val targets = scored.filter{ case (id, score) =>
      blackList.map(!_.contains(id)).getOrElse(true)
    }.top(query.start + query.size).drop(query.start)

    val itemScores = targets.map { case (i, s) =>
      new ItemScore(
        item = model.itemIntStringMap(i),
        score = s
      )
    }

    new PredictedResult(itemScores)
  }

  private def similarUser(items: Map[Int, Item], profiles: Set[Double]) = {
    val q = PriorityQueue[(Int, Double)]()
    for (k <- items) {
      if (q.size < ap.similarSize)
        q.enqueue((k._1, featureDistance(k._2.profiles, profiles.toList)))
      else {
        val tmpDistance = featureDistance(k._2.profiles, profiles.toList)
        if (tmpDistance < q.head._2) {
          q.dequeue()
          q.enqueue((k._1, tmpDistance))
        }
      }
    }

    q.dequeueAll.toSeq.reverse
  }

  private def featureDistance(org: Option[List[Double]], dst: List[Double]) = {
    org.map { lv =>
      lv.zip(dst).map { case (a, b) => (a - b) * (a - b) }.reduce(_ + _)
    } getOrElse Double.MaxValue
  }
}
