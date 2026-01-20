site:
    name: local
    max_threads: 3
#site:
#    name: cori-batch
#    image: ghcr.io/lsstdesc/txpipe-dev
#all the following steps should not depend on where you run
launcher:
    name: mini
    interval: 0.5
modules: >
    txpipe
    txpipe.extensions.cluster_counts.ingest 
    rail.estimation.algos.bpz_lite
    rail.creation.degraders.grid_selection
    rail.creation.engines.flowEngine
    rail.estimation.algos.nz_dir
    rail.estimation.algos.bpz_lite
python_paths: []
stages:
  #- name: CLIngestWazpDC2 # This will Ingest the cluster catalog from GCR
  #  nprocess: 1
  #- name: TXIngestDataPreview02
  #  nprocess: 1 # This does not work with MPI
  #- name: TXShearCalibration # This has to take the galaxy catalog with shear and calibrate it.
  # - name: FlowCreator       # Simulate a spectroscopic population. Prepares the model. This and the next two stages are responsible for generating a spec-z sample for the BPZ algorithm. THis will compute a pdf(z) for the galaxies to be used to compute the shear profile
  #   nprocess: 1
  #   aliases:
  #       output: ideal_specz_catalog
  #       model: flow
  # - name: GridSelection             # Simulate a spectroscopic sample from the model defined above. 
  #   nprocess: 1
  #   aliases:
  #       input: ideal_specz_catalog
  #       output: specz_catalog_pq
  # - name: TXParquetToHDF            # Convert to HDF5
  #   nprocess: 1
  #   aliases:
  #       input: specz_catalog_pq
  #       output: spectroscopic_catalog
  #- name: TXSourceSelectorMetadetect
  #  nprocess: 60
  - name: TXSourceSelectorSimple
    nprocess: 1
    threads_per_process: 1
  - name: BPZliteInformer
    nprocess: 1
    aliases:
        input: spectroscopic_catalog
        model: photoz_model
  - name: BPZliteEstimator
    nprocess: 30
    aliases:
        model: photoz_model
        input: photometry_catalog
        output: source_photoz_pdfs
  - name: CLClusterBinningRedshiftRichness
    nprocess: 1
  - name: CLClusterShearCatalogs
    nprocess: 30   #>1 does not work with mpi
  - name: CLClusterEnsembleProfiles
    nprocess: 3
  - name: CLClusterSACC
    nprocess: 1
    aliases:
        cluster_profiles: cluster_profiles
#    - name: CLClusterDataVector
#      nprocess: 1
output_dir: /sps/lsst/groups/clusters/cl_pipeline_project/TXPipe_data/dc2/outputs/
# Put the logs from the individual stages in this directory:
log_dir: ./logs

# Put the logs from the individual stages in this directory:
config: ./cosmodc2_config_in2p3.yml
inputs:
    # See README for paths to download these files
    shear_catalog: /sps/lsst/groups/clusters/cl_pipeline_project/TXPipe_data/dc2/shear_catalog.hdf5
    photometry_catalog:  /sps/lsst/groups/clusters/cl_pipeline_project/TXPipe_data/dc2/photometry_catalog.hdf5
    fiducial_cosmology: /sps/lsst/groups/clusters/cl_pipeline_project/TXPipe_data/cosmodc2/fiducial_cosmology.yml
    calibration_table: /sps/lsst/groups/clusters/cl_pipeline_project/TXPipe_data/cosmodc2/20deg2/sample_cosmodc2_w10year_errors.dat
    spectroscopic_catalog: /sps/lsst/groups/clusters/cl_pipeline_project/TXPipe_data/cosmodc2/20deg2/spectroscopic_catalog.hdf5
    cluster_catalog: /sps/lsst/groups/clusters/cl_pipeline_project/TXPipe_data/dc2/wazp_dc2_cluster_catalog.hdf5
    #shear_tomography_catalog: ./data/example/outputs_metadetect/shear_tomography_catalog.hdf5
    #source_photoz_pdfs: ./data/example/inputs/photoz_pdfs.hdf5
resume: true
pipeline_log: ./logs/log_full.txt
