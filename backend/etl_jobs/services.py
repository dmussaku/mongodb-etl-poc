import logging
from django.utils import timezone
from .models import Pipeline, JobExecution
from .pipeline import run_pipeline

logger = logging.getLogger(__name__)


class PipelineExecutionService:
    """Service class for executing ETL pipelines"""
    
    def __init__(self, pipeline_id):
        self.pipeline_id = pipeline_id
        self.pipeline = None
        self.execution = None
    
    def execute(self):
        """Execute the pipeline and return result"""
        try:
            self._load_pipeline()
            self._create_execution()
            load_info = self._run_pipeline()
            self._handle_success(load_info)
            return self._success_result()
            
        except Pipeline.DoesNotExist:
            return self._pipeline_not_found_result()
        except Exception as e:
            return self._handle_failure(e)
    
    def _load_pipeline(self):
        """Load and validate pipeline"""
        self.pipeline = Pipeline.objects.get(
            id=self.pipeline_id, 
            is_active=True, 
            is_enabled=True
        )
        logger.info(f"Starting pipeline execution for: {self.pipeline.name}")
    
    def _create_execution(self):
        """Create execution record"""
        self.execution = JobExecution.objects.create(pipeline=self.pipeline)
        self.execution.start_execution()
    
    def _run_pipeline(self):
        """Execute the actual pipeline"""
        return run_pipeline(
            source_config=self.pipeline.get_source_config(),
            destination_config=self.pipeline.get_destination_config(),
            pipeline_name=self.pipeline.name,
            dev_mode=False
        )
    
    def _handle_success(self, load_info):
        """Handle successful execution"""
        self.execution.complete_success(load_info)
        duration = float(self.execution.duration_seconds or 0)
        logger.info(f"Pipeline {self.pipeline.name} completed successfully in {duration:.2f} seconds")
    
    def _handle_failure(self, error):
        """Handle failed execution"""
        error_msg = f"Pipeline execution failed: {str(error)}"
        logger.error(error_msg, exc_info=True)
        
        if self.execution:
            self.execution.complete_failure(error_msg)
        
        return {
            "status": "failed", 
            "error": error_msg,
            "execution_id": self.execution.execution_id if self.execution else None
        }
    
    def _success_result(self):
        """Return success result"""
        return {
            "status": "success",
            "execution_id": self.execution.execution_id,
            "duration_seconds": float(self.execution.duration_seconds or 0)
        }
    
    def _pipeline_not_found_result(self):
        """Return pipeline not found result"""
        error_msg = f"Pipeline with ID {self.pipeline_id} not found or not active/enabled"
        logger.error(error_msg)
        return {"status": "failed", "error": error_msg}