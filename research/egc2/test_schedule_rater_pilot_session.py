import copy, importlib.util, pathlib, unittest
ROOT=pathlib.Path(__file__).resolve().parent

def load(name,file):
    spec=importlib.util.spec_from_file_location(name,ROOT/file)
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

gen=load("gen","generate_rater_pilot_assignment.py")
sched=load("sched","schedule_rater_pilot_session.py")

class SessionScheduleTests(unittest.TestCase):
    def setUp(self):
        self.source=gen.generate()
        self.result=sched.schedule_assignment(self.source,seed=20260725,min_repeat_gap=18)

    def test_validation_passes(self):
        self.assertTrue(self.result["validation"]["passed"],self.result["validation"])

    def test_rater_queue_conceals_type(self):
        for queue in self.result["rater_queues"].values():
            for row in queue:
                self.assertEqual(set(row),{"presentation_id","position"})

    def test_repeat_gap(self):
        for rater in self.source["design"]["rater_ids"]:
            rows=sorted([x for x in self.result["audit_schedule"] if x["rater_id"]==rater],key=lambda x:x["position"])
            source_positions={x["stimulus_ref"]:x["position"] for x in rows if x["assignment_type"]=="primary_response"}
            for row in rows:
                if row["assignment_type"]=="blind_repeat":
                    self.assertGreaterEqual(row["position"]-source_positions[row["repeat_of_response_id"]],18)

    def test_deterministic(self):
        other=sched.schedule_assignment(self.source,seed=20260725,min_repeat_gap=18)
        self.assertEqual(self.result["content_sha256"],other["content_sha256"])

    def test_one_and_two_dropout_graphs_connected(self):
        summary=self.result["dropout_robustness"]["summary_by_dropout_count"]
        self.assertTrue(summary["1"]["all_connected"])
        self.assertTrue(summary["2"]["all_connected"])
        self.assertEqual(summary["1"]["minimum_remaining_ratings"],3)
        self.assertEqual(summary["2"]["minimum_remaining_ratings"],2)

    def test_metadata_leak_detected(self):
        bad=copy.deepcopy(self.result)
        first=next(iter(bad["rater_queues"]))
        bad["rater_queues"][first][0]["assignment_type"]="anchor"
        self.assertIn("RATER_QUEUE_LEAKS_ITEM_METADATA",sched.validate_schedule(self.source,bad)["errors"])

    def test_repeat_gap_violation_detected(self):
        bad=copy.deepcopy(self.result)
        rater=next(x["rater_id"] for x in bad["audit_schedule"] if x["assignment_type"]=="blind_repeat")
        rows=[x for x in bad["audit_schedule"] if x["rater_id"]==rater]
        repeat=next(x for x in rows if x["assignment_type"]=="blind_repeat")
        source=next(x for x in rows if x["assignment_type"]=="primary_response" and x["stimulus_ref"]==repeat["repeat_of_response_id"])
        repeat["position"]=source["position"]+1
        self.assertTrue(any(e.startswith("REPEAT_GAP") for e in sched.validate_schedule(self.source,bad)["errors"]))

if __name__=="__main__": unittest.main()
