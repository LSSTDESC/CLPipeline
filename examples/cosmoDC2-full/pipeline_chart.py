import ceci
# Read the appropriate pipeline configuration, and ask for a flow-chart.

pipeline_file = "/sps/lsst/users/ebarroso/CLPipeline/examples/cosmoDC2-full/CL_pipline_txpipe.yml"
# pipeline_file = "examples/cosmodc2/Cluster_pipelines/pipeline-20deg2-CL-nersc.yml"
flowchart_file = "/sps/lsst/users/ebarroso/CLPipeline/examples/cosmoDC2-full/CL_pipeline.png"



pipeline_config = ceci.Pipeline.build_config(pipeline_file, flow_chart=flowchart_file, dry_run=True)
ceci.run_pipeline(pipeline_config);
