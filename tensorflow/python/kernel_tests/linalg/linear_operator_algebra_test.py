# Copyright 2018 The TensorFlow Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================
"""Tests for registration mechanisms."""

from tensorflow.python.framework import tensor_shape
from tensorflow.python.ops.linalg import linear_operator
from tensorflow.python.ops.linalg import linear_operator_algebra
from tensorflow.python.ops.linalg import solve_registrations  # pylint: disable=unused-import
from tensorflow.python.platform import test

# pylint: disable=protected-access
_SOLVE = linear_operator_algebra._SOLVE
_registered_solve = linear_operator_algebra._registered_solve
# pylint: enable=protected-access


class SolveTest(test.TestCase):

  def testRegistration(self):

    class CustomLinOp(linear_operator.LinearOperator):

      def _matmul(self, a):
        pass

      def _solve(self, a):
        pass

      def _shape(self):
        return tensor_shape.TensorShape([1, 1])

      def _shape_tensor(self):
        pass

    # Register Solve to a lambda that spits out the name parameter
    @linear_operator_algebra.RegisterSolve(CustomLinOp, CustomLinOp)
    def _solve(a, b):  # pylint: disable=unused-argument,unused-variable
      return "OK"

    custom_linop = CustomLinOp(
        dtype=None, is_self_adjoint=True, is_positive_definite=True)
    self.assertEqual("OK", custom_linop.solve(custom_linop))

  def testRegistrationFailures(self):

    class CustomLinOp(linear_operator.LinearOperator):
      pass

    with self.assertRaisesRegex(TypeError, "must be callable"):
      linear_operator_algebra.RegisterSolve(CustomLinOp, CustomLinOp)("blah")

    # First registration is OK
    linear_operator_algebra.RegisterSolve(
        CustomLinOp, CustomLinOp)(lambda a: None)

    # Second registration fails
    with self.assertRaisesRegex(ValueError, "has already been registered"):
      linear_operator_algebra.RegisterSolve(
          CustomLinOp, CustomLinOp)(lambda a: None)

  def testExactSolveRegistrationsAllMatch(self):
    for (k, v) in _SOLVE.items():
      self.assertEqual(v, _registered_solve(k[0], k[1]))


if __name__ == "__main__":
  test.main()
