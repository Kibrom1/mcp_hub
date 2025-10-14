"""
Performance monitoring and metrics collection for MCP Hub Core
"""

import time
import psutil
import threading
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from collections import defaultdict, deque
from dataclasses import dataclass, asdict
import logging
from functools import wraps
import json

logger = logging.getLogger(__name__)

@dataclass
class Metric:
    """Metric data structure"""
    name: str
    value: float
    timestamp: datetime
    tags: Dict[str, str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'name': self.name,
            'value': self.value,
            'timestamp': self.timestamp.isoformat(),
            'tags': self.tags or {}
        }

@dataclass
class PerformanceStats:
    """Performance statistics"""
    request_count: int = 0
    total_response_time: float = 0.0
    min_response_time: float = float('inf')
    max_response_time: float = 0.0
    error_count: int = 0
    success_count: int = 0
    
    @property
    def average_response_time(self) -> float:
        if self.request_count == 0:
            return 0.0
        return self.total_response_time / self.request_count
    
    @property
    def success_rate(self) -> float:
        if self.request_count == 0:
            return 0.0
        return self.success_count / self.request_count
    
    @property
    def error_rate(self) -> float:
        if self.request_count == 0:
            return 0.0
        return self.error_count / self.request_count

class MetricsCollector:
    """Collects and stores application metrics"""
    
    def __init__(self, max_metrics: int = 10000):
        self.max_metrics = max_metrics
        self.metrics: deque = deque(maxlen=max_metrics)
        self.stats: Dict[str, PerformanceStats] = defaultdict(PerformanceStats)
        self.lock = threading.Lock()
    
    def add_metric(self, name: str, value: float, tags: Dict[str, str] = None):
        """Add a metric"""
        with self.lock:
            metric = Metric(
                name=name,
                value=value,
                timestamp=datetime.now(),
                tags=tags or {}
            )
            self.metrics.append(metric)
    
    def record_request(self, endpoint: str, response_time: float, success: bool = True):
        """Record API request metrics"""
        with self.lock:
            stats = self.stats[endpoint]
            stats.request_count += 1
            stats.total_response_time += response_time
            stats.min_response_time = min(stats.min_response_time, response_time)
            stats.max_response_time = max(stats.max_response_time, response_time)
            
            if success:
                stats.success_count += 1
            else:
                stats.error_count += 1
    
    def get_metrics(self, name: str = None, tags: Dict[str, str] = None, 
                   start_time: datetime = None, end_time: datetime = None) -> List[Metric]:
        """Get metrics with optional filtering"""
        with self.lock:
            filtered_metrics = []
            
            for metric in self.metrics:
                # Filter by name
                if name and metric.name != name:
                    continue
                
                # Filter by tags
                if tags:
                    if not all(metric.tags.get(k) == v for k, v in tags.items()):
                        continue
                
                # Filter by time range
                if start_time and metric.timestamp < start_time:
                    continue
                if end_time and metric.timestamp > end_time:
                    continue
                
                filtered_metrics.append(metric)
            
            return filtered_metrics
    
    def get_stats(self, endpoint: str = None) -> Dict[str, PerformanceStats]:
        """Get performance statistics"""
        with self.lock:
            if endpoint:
                return {endpoint: self.stats[endpoint]}
            return dict(self.stats)
    
    def clear_metrics(self):
        """Clear all metrics"""
        with self.lock:
            self.metrics.clear()
            self.stats.clear()

class SystemMonitor:
    """System resource monitoring"""
    
    def __init__(self):
        self.process = psutil.Process()
        self.start_time = datetime.now()
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """Get current system metrics"""
        try:
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            
            # Memory metrics
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            memory_available = memory.available
            memory_total = memory.total
            
            # Process metrics
            process_memory = self.process.memory_info()
            process_cpu = self.process.cpu_percent()
            
            # Disk metrics
            disk = psutil.disk_usage('/')
            disk_percent = disk.percent
            disk_free = disk.free
            disk_total = disk.total
            
            # Network metrics
            network = psutil.net_io_counters()
            
            return {
                'timestamp': datetime.now().isoformat(),
                'cpu': {
                    'percent': cpu_percent,
                    'count': cpu_count
                },
                'memory': {
                    'percent': memory_percent,
                    'available': memory_available,
                    'total': memory_total,
                    'process_memory': process_memory.rss,
                    'process_memory_percent': process_memory.percent
                },
                'disk': {
                    'percent': disk_percent,
                    'free': disk_free,
                    'total': disk_total
                },
                'network': {
                    'bytes_sent': network.bytes_sent,
                    'bytes_recv': network.bytes_recv,
                    'packets_sent': network.packets_sent,
                    'packets_recv': network.packets_recv
                },
                'process': {
                    'cpu_percent': process_cpu,
                    'memory_rss': process_memory.rss,
                    'memory_vms': process_memory.vms,
                    'num_threads': self.process.num_threads(),
                    'create_time': self.process.create_time()
                },
                'uptime': (datetime.now() - self.start_time).total_seconds()
            }
        except Exception as e:
            logger.error(f"Error getting system metrics: {e}")
            return {}
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get system health status"""
        try:
            metrics = self.get_system_metrics()
            
            # Health checks
            health_checks = {
                'cpu_healthy': metrics.get('cpu', {}).get('percent', 0) < 80,
                'memory_healthy': metrics.get('memory', {}).get('percent', 0) < 80,
                'disk_healthy': metrics.get('disk', {}).get('percent', 0) < 90,
                'process_healthy': True  # Add more specific checks
            }
            
            overall_healthy = all(health_checks.values())
            
            return {
                'healthy': overall_healthy,
                'checks': health_checks,
                'metrics': metrics,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting health status: {e}")
            return {
                'healthy': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }

class PerformanceMonitor:
    """Main performance monitoring class"""
    
    def __init__(self):
        self.metrics_collector = MetricsCollector()
        self.system_monitor = SystemMonitor()
        self.start_time = datetime.now()
    
    def record_api_call(self, endpoint: str, method: str, response_time: float, 
                       status_code: int, user_id: str = None):
        """Record API call metrics"""
        success = 200 <= status_code < 400
        
        # Record request metrics
        self.metrics_collector.record_request(endpoint, response_time, success)
        
        # Add detailed metrics
        tags = {
            'endpoint': endpoint,
            'method': method,
            'status_code': str(status_code)
        }
        if user_id:
            tags['user_id'] = user_id
        
        self.metrics_collector.add_metric('api_response_time', response_time, tags)
        self.metrics_collector.add_metric('api_requests_total', 1, tags)
        
        if not success:
            self.metrics_collector.add_metric('api_errors_total', 1, tags)
    
    def record_llm_call(self, provider: str, model: str, response_time: float, 
                       tokens_used: int = None, success: bool = True):
        """Record LLM call metrics"""
        tags = {
            'provider': provider,
            'model': model,
            'success': str(success)
        }
        
        self.metrics_collector.add_metric('llm_response_time', response_time, tags)
        self.metrics_collector.add_metric('llm_requests_total', 1, tags)
        
        if tokens_used:
            self.metrics_collector.add_metric('llm_tokens_used', tokens_used, tags)
        
        if not success:
            self.metrics_collector.add_metric('llm_errors_total', 1, tags)
    
    def record_tool_execution(self, tool_name: str, server_name: str, 
                            execution_time: float, success: bool = True):
        """Record tool execution metrics"""
        tags = {
            'tool_name': tool_name,
            'server_name': server_name,
            'success': str(success)
        }
        
        self.metrics_collector.add_metric('tool_execution_time', execution_time, tags)
        self.metrics_collector.add_metric('tool_executions_total', 1, tags)
        
        if not success:
            self.metrics_collector.add_metric('tool_errors_total', 1, tags)
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get comprehensive performance summary"""
        return {
            'uptime': (datetime.now() - self.start_time).total_seconds(),
            'system_metrics': self.system_monitor.get_system_metrics(),
            'health_status': self.system_monitor.get_health_status(),
            'api_stats': self.metrics_collector.get_stats(),
            'recent_metrics': [
                metric.to_dict() for metric in 
                self.metrics_collector.get_metrics()[-100:]  # Last 100 metrics
            ]
        }
    
    def get_metrics_summary(self, time_window: int = 3600) -> Dict[str, Any]:
        """Get metrics summary for specified time window"""
        end_time = datetime.now()
        start_time = end_time - timedelta(seconds=time_window)
        
        recent_metrics = self.metrics_collector.get_metrics(
            start_time=start_time, 
            end_time=end_time
        )
        
        # Group metrics by name
        metrics_by_name = defaultdict(list)
        for metric in recent_metrics:
            metrics_by_name[metric.name].append(metric.value)
        
        # Calculate summaries
        summaries = {}
        for name, values in metrics_by_name.items():
            if values:
                summaries[name] = {
                    'count': len(values),
                    'min': min(values),
                    'max': max(values),
                    'avg': sum(values) / len(values),
                    'total': sum(values)
                }
        
        return {
            'time_window': time_window,
            'start_time': start_time.isoformat(),
            'end_time': end_time.isoformat(),
            'summaries': summaries
        }

# Global performance monitor
performance_monitor = PerformanceMonitor()

# Monitoring decorators
def monitor_performance(metric_name: str = None, tags: Dict[str, str] = None):
    """Decorator to monitor function performance"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            success = True
            
            try:
                result = await func(*args, **kwargs)
                return result
            except Exception as e:
                success = False
                raise
            finally:
                execution_time = time.time() - start_time
                
                # Record metrics
                metric_name_final = metric_name or f"{func.__module__}.{func.__name__}"
                performance_monitor.metrics_collector.add_metric(
                    metric_name_final, 
                    execution_time, 
                    {**(tags or {}), 'success': str(success)}
                )
        
        return wrapper
    return decorator

def monitor_api_calls(endpoint: str = None):
    """Decorator to monitor API calls"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            success = True
            status_code = 200
            
            try:
                result = await func(*args, **kwargs)
                return result
            except Exception as e:
                success = False
                status_code = 500
                raise
            finally:
                execution_time = time.time() - start_time
                
                # Record API call metrics
                endpoint_name = endpoint or func.__name__
                performance_monitor.record_api_call(
                    endpoint_name,
                    'POST',  # Default method
                    execution_time,
                    status_code
                )
        
        return wrapper
    return decorator

def monitor_llm_calls(provider: str = None):
    """Decorator to monitor LLM calls"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            success = True
            tokens_used = None
            
            try:
                result = await func(*args, **kwargs)
                
                # Extract tokens_used if available
                if hasattr(result, 'tokens_used'):
                    tokens_used = result.tokens_used
                
                return result
            except Exception as e:
                success = False
                raise
            finally:
                execution_time = time.time() - start_time
                
                # Record LLM call metrics
                provider_name = provider or 'unknown'
                model_name = kwargs.get('model', 'unknown')
                
                performance_monitor.record_llm_call(
                    provider_name,
                    model_name,
                    execution_time,
                    tokens_used,
                    success
                )
        
        return wrapper
    return decorator

def monitor_tool_executions():
    """Decorator to monitor tool executions"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            success = True
            
            # Extract tool information
            tool_name = kwargs.get('tool_name', func.__name__)
            server_name = kwargs.get('server_name', 'unknown')
            
            try:
                result = await func(*args, **kwargs)
                return result
            except Exception as e:
                success = False
                raise
            finally:
                execution_time = time.time() - start_time
                
                # Record tool execution metrics
                performance_monitor.record_tool_execution(
                    tool_name,
                    server_name,
                    execution_time,
                    success
                )
        
        return wrapper
    return decorator
