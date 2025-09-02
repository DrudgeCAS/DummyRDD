# -*- coding: utf-8 -*-

import unittest

from dummy_spark import RDD
from dummy_spark import SparkContext
from dummy_spark import SparkConf


class RDDTests (unittest.TestCase):

    SPARK_CONTEXT = SparkContext(master='', conf=SparkConf())
    TEST_RANGES = [
        (0, 0, 1),
        (0, 10, 1),
        (0, 10, 2),
        (0, 100, 13),
        (0, 1000, 17),
        (0, 10000, 31),
    ]
    SAMPLE_FRACTION = 0.10
    SAMPLE_SEED = 1234

    def test_init(self):
        for start, stop, step in self.TEST_RANGES:
            l = list(range(start, stop, step))
            rdd = RDD(l, self.SPARK_CONTEXT)
            self.assertEqual(l, rdd.collect())

            s = set(range(100))
            rdd = RDD(s, self.SPARK_CONTEXT)
            self.assertEqual(sorted(list(s)), sorted(rdd.collect()))

        t = (1, 2, 3)
        with self.assertRaises(AttributeError):
            RDD(t, self.SPARK_CONTEXT)

        with self.assertRaises(AttributeError):
            RDD('', self.SPARK_CONTEXT)

    def test_ctx(self):
        rdd = RDD([], self.SPARK_CONTEXT)
        self.assertEqual(rdd.ctx, self.SPARK_CONTEXT)

    @staticmethod
    def square(x):
        return x**2

    def test_map(self):
        for start, stop, step in self.TEST_RANGES:
            l1 = range(start, stop, step)
            l2 = map(RDDTests.square, l1)
            rdd = RDD(list(l1), self.SPARK_CONTEXT)
            rdd = rdd.map(RDDTests.square)
            self.assertEqual(rdd.collect(), list(l2))

    @staticmethod
    def triplicate(x):
        return [x, x, x]

    def test_flat_map(self):
        for start, stop, step in self.TEST_RANGES:
            l1 = range(start, stop, step)
            l2 = map(RDDTests.triplicate, l1)
            l3 = []
            for sl in l2:
                l3.extend(sl)
            rdd = RDD(list(l1), self.SPARK_CONTEXT)
            rdd = rdd.flatMap(RDDTests.triplicate)
            self.assertEqual(rdd.collect(), list(l3))

    @staticmethod
    def is_square(x):
        return x == x**2

    def test_filter(self):
        for start, stop, step in self.TEST_RANGES:
            l1 = range(start, stop, step)
            l2 = filter(RDDTests.is_square, l1)
            rdd = RDD(list(l1), self.SPARK_CONTEXT)
            rdd = rdd.filter(RDDTests.is_square)
            self.assertEqual(rdd.collect(), list(l2))

    @staticmethod
    def return_one(x):
        return x - x + 1

    def test_distinct(self):
        for start, stop, step in self.TEST_RANGES:
            l = range(start, stop, step)
            rdd = RDD(list(l), self.SPARK_CONTEXT)
            rdd = rdd.map(RDDTests.return_one)
            rdd = rdd.distinct()
            if len(l) > 0:
                self.assertEqual(rdd.collect(), [1])
            else:
                self.assertEqual(rdd.collect(), [])

    def test_sample_with_replacement(self):
        for start, stop, step in self.TEST_RANGES:
            l = range(start, stop, step)
            rdd = RDD(list(l), self.SPARK_CONTEXT)
            sample = rdd.sample(True, self.SAMPLE_FRACTION).collect()
            self.assertEqual(len(sample), int(len(l) * self.SAMPLE_FRACTION))
            for item in sample:
                self.assertTrue(item in l)

    def test_sample_with_replacement_with_seed(self):
        for start, stop, step in self.TEST_RANGES:
            l = range(start, stop, step)
            rdd = RDD(list(l), self.SPARK_CONTEXT)
            sample1 = rdd.sample(True, self.SAMPLE_FRACTION, self.SAMPLE_SEED).collect()
            sample2 = rdd.sample(True, self.SAMPLE_FRACTION, self.SAMPLE_SEED).collect()
            self.assertEqual(sorted(sample1), sorted(sample2))
            sample = sample1
            self.assertEqual(len(sample), int(len(l) * self.SAMPLE_FRACTION))
            for item in sample:
                self.assertTrue(item in l)

    def test_sample_without_replacement(self):
        for start, stop, step in self.TEST_RANGES:
            l = range(start, stop, step)
            rdd = RDD(list(l), self.SPARK_CONTEXT)
            sample = rdd.sample(False, self.SAMPLE_FRACTION).collect()
            self.assertEqual(len(sample), int(len(l) * self.SAMPLE_FRACTION))
            self.assertEqual(sorted(l), sorted(set(l)))
            for item in sample:
                self.assertTrue(item in l)

    def test_sample_without_replacement_with_seed(self):
        for start, stop, step in self.TEST_RANGES:
            l = range(start, stop, step)
            rdd = RDD(list(l), self.SPARK_CONTEXT)
            sample1 = rdd.sample(False, self.SAMPLE_FRACTION, self.SAMPLE_SEED).collect()
            sample2 = rdd.sample(False, self.SAMPLE_FRACTION, self.SAMPLE_SEED).collect()
            self.assertEqual(sorted(sample1), sorted(sample2))
            sample = sample1
            self.assertEqual(len(sample), int(len(l) * self.SAMPLE_FRACTION))
            self.assertEqual(sorted(l), sorted(set(l)))
            for item in sample:
                self.assertTrue(item in l)

    def test_union(self):
        for start1, stop1, step1 in self.TEST_RANGES:
            for start2, stop2, step2 in self.TEST_RANGES:
                l1 = range(start1, stop1, step1)
                l2 = range(start2, stop2, step2)
                rdd1 = RDD(list(l1), self.SPARK_CONTEXT)
                rdd2 = RDD(list(l2), self.SPARK_CONTEXT)
                rdd = rdd1.union(rdd2)
                self.assertEqual(sorted(rdd.collect()), sorted(list(l1) + list(l2)))

    def test_intersection(self):
        for start1, stop1, step1 in self.TEST_RANGES:
            for start2, stop2, step2 in self.TEST_RANGES:
                l1 = range(start1, stop1, step1)
                l2 = range(start2, stop2, step2)
                rdd1 = RDD(list(l1), self.SPARK_CONTEXT)
                rdd2 = RDD(list(l2), self.SPARK_CONTEXT)
                rdd = rdd1.intersection(rdd2)
                self.assertEqual(sorted(rdd.collect()), sorted([x for x in l1 if x in l2]))

    def test_group_by_key(self):
        l = [(1, 1), (2, 1), (2, 2), (3, 1), (3, 2), (3, 3)]
        rdd = RDD(l, self.SPARK_CONTEXT)
        rdd = rdd.groupByKey()
        r = rdd.collect()
        r = [(kv[0], list(kv[1])) for kv in r]
        self.assertEqual(sorted(r), sorted([(1, [1]), (2, [1, 2]), (3, [1, 2, 3])]))

    def test_reduce_by_key(self):
        l = [(1, 1), (2, 1), (2, 2), (3, 1), (3, 2), (3, 3)]
        rdd = RDD(l, self.SPARK_CONTEXT)
        rdd = rdd.reduceByKey(lambda a, b: a + b)
        self.assertEqual(sorted(rdd.collect()), sorted([(1, 1), (2, 3), (3, 6)]))

    def test_cartesian(self):
        for start1, stop1, step1 in self.TEST_RANGES:
            for start2, stop2, step2 in self.TEST_RANGES:
                l1 = range(start1, stop1, step1)
                l2 = range(start2, stop2, step2)
                rdd1 = RDD(list(l1), self.SPARK_CONTEXT)
                rdd2 = RDD(list(l2), self.SPARK_CONTEXT)
                rdd = rdd1.cartesian(rdd2)
                r = rdd.collect()
                self.assertEqual(len(r), len(l1) * len(l2))
                for t, u in r:
                    self.assertTrue(t in l1)
                    self.assertTrue(u in l2)

    def test_cogroup(self):
        l1 = [(1, 1), (2, 1), (2, 2), (3, 1), (3, 2), (3, 3)]
        l2 = [(2, 10), (2, 20), (3, 10), (3, 20), (3, 30), (4, 40)]
        rdd1 = RDD(l1, self.SPARK_CONTEXT)
        rdd2 = RDD(l2, self.SPARK_CONTEXT)
        rdd = rdd1.cogroup(rdd2)
        l = rdd.collect()
        self.assertEqual(
            sorted(l),
            sorted([(1, [1], []), (2, [1, 2], [10, 20]), (3, [1, 2, 3], [10, 20, 30]), (4, [], [40])])
        )

    def test_word_count_1(self):

        lines = [
            'grape banana apple',
        ]

        expected_output = [
            ('apple', 1),
            ('banana', 1),
            ('grape', 1),
        ]

        sc = SparkContext(master='', conf=SparkConf())

        rdd = sc.parallelize(lines)
        rdd = rdd.flatMap(lambda x: x.split(' '))
        rdd = rdd.map(lambda word: (word, 1))
        rdd = rdd.reduceByKey(lambda a, b: a + b)

        output = rdd.collect()
        self.assertEqual(sorted(output), sorted(expected_output))

    def test_word_count_2(self):

        lines = [
            'apple',
            'apple banana',
            'apple banana',
            'apple banana grape',
        ]

        expected_output = [
            ('apple', 4),
            ('banana', 3),
            ('grape', 1),
        ]

        sc = SparkContext(master='', conf=SparkConf())

        rdd = sc.parallelize(lines)
        rdd = rdd.flatMap(lambda x: x.split(' '))
        rdd = rdd.map(lambda word: (word, 1))
        rdd = rdd.reduceByKey(lambda a, b: a + b)

        output = rdd.collect()
        self.assertEqual(sorted(output), sorted(expected_output))

    def test_word_count_3(self):

        lines = [
            'apple',
            'apple banana',
            'apple banana',
            'apple banana grape',
            'banana grape',
            'banana'
        ]

        expected_output = [
            ('apple', 4),
            ('banana', 5),
            ('grape', 2),
        ]

        sc = SparkContext(master='', conf=SparkConf())

        rdd = sc.parallelize(lines)
        rdd = rdd.flatMap(lambda x: x.split(' '))
        rdd = rdd.map(lambda word: (word, 1))
        rdd = rdd.reduceByKey(lambda a, b: a + b)

        output = rdd.collect()
        self.assertEqual(sorted(output), sorted(expected_output))

    def test_left_outer_join(self):
        sc = SparkContext(master='', conf=SparkConf())
        rdd1 = sc.parallelize([('A', [1, 2, 3]), ('B', [2,3,4])])
        rdd2 = sc.parallelize([('A', [1, 2, 3]), ('B', [2,3,4]), ('B', [4,5,6])])
        out = rdd1.leftOuterJoin(rdd2).collect()
        self.assertEqual(len(out), 3)

    def test_not_implemented_methods(self):
        sc = SparkContext(master='', conf=SparkConf())
        rdd = sc.parallelize([])

        with self.assertRaises(NotImplementedError):
            rdd._pickled()

        with self.assertRaises(NotImplementedError):
            rdd.mapPartitionsWithIndex(None, None,)

        with self.assertRaises(NotImplementedError):
            rdd._computeFractionForSampleSize(None, None, None)

        with self.assertRaises(NotImplementedError):
            rdd.pipe(None, None)

        with self.assertRaises(NotImplementedError):
            rdd.reduce(None)

        with self.assertRaises(NotImplementedError):
            rdd.treeReduce(None, None)

        with self.assertRaises(NotImplementedError):
            rdd.fold(None, None,)

        with self.assertRaises(NotImplementedError):
            rdd.aggregate(None, None, None)

        with self.assertRaises(NotImplementedError):
            rdd.treeAggregate(None, None, None, None)

        with self.assertRaises(NotImplementedError):
            rdd.stats()

        with self.assertRaises(NotImplementedError):
            rdd.histogram(None)

        with self.assertRaises(NotImplementedError):
            rdd.variance()

        with self.assertRaises(NotImplementedError):
            rdd.stdev()

        with self.assertRaises(NotImplementedError):
            rdd.sampleStdev()

        with self.assertRaises(NotImplementedError):
            rdd.sampleVariance()

        with self.assertRaises(NotImplementedError):
            rdd.countByValue()

        with self.assertRaises(NotImplementedError):
            rdd.top(None, None)

        with self.assertRaises(NotImplementedError):
            rdd.takeOrdered(None, None)

        with self.assertRaises(NotImplementedError):
            rdd.saveAsNewAPIHadoopDataset(None, None, None)

        with self.assertRaises(NotImplementedError):
            rdd.saveAsNewAPIHadoopFile(None, None, None, None, None, None, None)

        with self.assertRaises(NotImplementedError):
            rdd.saveAsHadoopDataset(None, None, None)

        with self.assertRaises(NotImplementedError):
            rdd.saveAsHadoopFile(None, None, None, None, None, None, None, None)

        with self.assertRaises(NotImplementedError):
            rdd.saveAsSequenceFile(None, None)

        with self.assertRaises(NotImplementedError):
            rdd.saveAsPickleFile(None, None)

        with self.assertRaises(NotImplementedError):
            rdd.saveAsTextFile(None, None)

        with self.assertRaises(NotImplementedError):
            rdd.collectAsMap()

        with self.assertRaises(NotImplementedError):
            rdd.keys()

        with self.assertRaises(NotImplementedError):
            rdd.values()

        with self.assertRaises(NotImplementedError):
            rdd.reduceByKeyLocally(None)

        with self.assertRaises(NotImplementedError):
            rdd.countByKey()

        with self.assertRaises(NotImplementedError):
            rdd.join(None, None)

        with self.assertRaises(NotImplementedError):
            rdd.rightOuterJoin(None, None)

        with self.assertRaises(NotImplementedError):
            rdd.fullOuterJoin(None, None)

        with self.assertRaises(NotImplementedError):
            rdd.combineByKey(None, None, None, None)

        with self.assertRaises(NotImplementedError):
            rdd.aggregateByKey(None, None, None, None)

        with self.assertRaises(NotImplementedError):
            rdd.foldByKey(None, None, None)

        with self.assertRaises(NotImplementedError):
            rdd._can_spill()

        with self.assertRaises(NotImplementedError):
            rdd._memory_limit()

        with self.assertRaises(NotImplementedError):
            rdd.groupWith(None, None)

        with self.assertRaises(NotImplementedError):
            rdd.sampleByKey(None, None, None)

        with self.assertRaises(NotImplementedError):
            rdd.subtractByKey(None, None)

        with self.assertRaises(NotImplementedError):
            rdd.subtract(None, None)

        with self.assertRaises(NotImplementedError):
            rdd.coalesce(None, None)

        with self.assertRaises(NotImplementedError):
            rdd.toDebugString()

        with self.assertRaises(NotImplementedError):
            rdd.getStorageLevel()

        with self.assertRaises(NotImplementedError):
            rdd._to_java_object_rdd()



