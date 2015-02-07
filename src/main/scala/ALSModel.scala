package org.apache.spark.mllib.recommendation

import com.jiaoew.recommander._
import io.prediction.controller.{IPersistentModel, IPersistentModelLoader}
import io.prediction.data.storage.BiMap
import org.apache.spark.SparkContext
import org.apache.spark.rdd.RDD

/**
 * Created by jiaoew on 15/2/1.
 */
class ALSModel(
                override val rank: Int,
                override val userFeatures: RDD[(Int, Array[Double])],
                override val productFeatures: RDD[(Int, Array[Double])],
                val itemStringIntMap: BiMap[String, Int],
                val items: Map[Int, Item]
                ) extends MatrixFactorizationModel(rank, userFeatures, productFeatures) with IPersistentModel[ALSAlgorithmParams] with Serializable {

  @transient lazy val itemIntStringMap = itemStringIntMap.inverse

  def save(id: String, params: ALSAlgorithmParams, sc: SparkContext): Boolean = {
    sc.parallelize(Seq(rank)).saveAsObjectFile(s"/tmp/${id}/rank")
    userFeatures.saveAsObjectFile(s"/tmp/${id}/userFeatures")
    productFeatures.saveAsObjectFile(s"/tmp/${id}/productFeatures")
    sc.parallelize(Seq(itemStringIntMap)).saveAsObjectFile(s"/tmp/${id}/itemStringIntMap")
    sc.parallelize(Seq(items)).saveAsObjectFile(s"/tmp/${id}/items")
    true
  }

  override def toString = {
    s" productFeatures: [${productFeatures.count()}]" +
      s"(${productFeatures.take(2).toList}...)" +
      s" itemStringIntMap: [${itemStringIntMap.size}]" +
      s"(${itemStringIntMap.take(2).toString}...)]" +
      s" items: [${items.size}]" +
      s"(${items.take(2).toString}...)]"
  }
}

object ALSModel extends IPersistentModelLoader[ALSAlgorithmParams, ALSModel] {
  def apply(id: String, params: ALSAlgorithmParams, sc: Option[SparkContext]) = {
    new ALSModel(
      rank = sc.get.objectFile[Int](s"/tmp/${id}/rank").first,
      userFeatures = sc.get.objectFile(s"/tmp/${id}/userFeatures"),
      productFeatures = sc.get.objectFile(s"/tmp/${id}/productFeatures"),
      itemStringIntMap = sc.get.objectFile[BiMap[String, Int]](s"/tmp/${id}/itemStringIntMap").first,
      items = sc.get.objectFile[Map[Int, Item]](s"/tmp/${id}/items").first)
  }
}

