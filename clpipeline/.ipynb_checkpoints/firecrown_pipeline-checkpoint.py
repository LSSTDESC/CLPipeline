#!/usr/bin/env python
#File dedicated to impement the Firecrown pipeline stage into ceci
from ceci_types import DataFile, TextFile
from ceci import PipelineStage
import sys
import firecrown

class FirecrownPipeline(PipelineStage):
    """
    This pipeline element is a template for Firecrown Likelihood construction
    """

    name = "FirecrownPipe"
    inputs = [("SACC", TextFile)]
    outputs = [("FirecrownLikelihood")]
    config_options = {"metacalibration": bool, "apply_flag": bool}

    def run(self):
        # Retrieve configuration:
        my_config = self.config
        print("Here is my configuration :", my_config)

        for inp, _ in self.inputs:
            filename = self.get_input(inp)
            print(f"    shearMeasurementPipe reading from {filename}")
            open(filename)

        for out, _ in self.outputs:
            filename = self.get_output(out)
            print(f"    shearMeasurementPipe writing to {filename}")
            open(filename, "w").write("shearMeasurementPipe was here \n")



test = FirecrownPipeline()
test.run()
