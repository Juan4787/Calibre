import xml.etree.ElementTree as ET

from qa.mutation import causal_assertion_failure


def test_mutant_verdict_requires_selected_causal_assertion():
    selectors = ["tests/test_engine.py::test_price"]
    signal = "At index 0 diff: 'FAIL' != 'PASS'"

    def report(case_name, node, body):
        root = ET.Element("testsuite")
        case = ET.SubElement(root, "testcase", name=case_name)
        ET.SubElement(case, node).text = body
        return root

    correct = report("test_price[boundary]", "failure", "AssertionError: assert x\n" + signal)
    assert causal_assertion_failure(correct, selectors, signal) == (True, ["test_price"])
    assert causal_assertion_failure(report("test_price", "error", signal), selectors, signal)[0] is False
    assert (
        causal_assertion_failure(report("test_other", "failure", "assert x\n" + signal), selectors, signal)[0]
        is False
    )
    assert (
        causal_assertion_failure(report("test_price", "failure", "assert digest == old"), selectors, signal)[
            0
        ]
        is False
    )
