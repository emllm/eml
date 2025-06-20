import argparse
import sys
from typing import List, Dict, Any
import peml
from peml.core import PEMLParser, PEMLError
from peml.validator import PEMLValidator
import json

class PEMLCLI:
    def __init__(self):
        self.parser = argparse.ArgumentParser(
            description='PEML Language Command Line Interface'
        )
        self.parser.add_argument('--validate', action='store_true',
            help='Validate message structure')
        self._setup_parser()

    def _setup_parser(self):
        subparsers = self.parser.add_subparsers(dest='command')
        
        # Interactive mode
        interactive = subparsers.add_parser('interactive', 
            help='Start interactive EML shell')
        
        # Parse message
        parse = subparsers.add_parser('parse',
            help='Parse PEML content')
        parse.add_argument('content', nargs='?',
            help='PEML content to parse')
        
        # Generate message
        generate = subparsers.add_parser('generate',
            help='Generate PEML from dictionary')
        generate.add_argument('--input', '-i', required=True,
            help='Input JSON file containing message structure')
        
        # Validate message
        validate = subparsers.add_parser('validate',
            help='Validate PEML message structure')
        validate.add_argument('content',
            help='PEML content to validate')
        
        # Convert message
        convert = subparsers.add_parser('convert',
            help='Convert between formats')
        convert.add_argument('--from', dest='from_format', required=True,
            choices=['peml', 'json'],
            help='Input format')
        convert.add_argument('--to', dest='to_format', required=True,
            choices=['peml', 'json'],
            help='Output format')
        convert.add_argument('--input', '-i', required=True,
            help='Input file')
        convert.add_argument('--output', '-o',
            help='Output file')
        
        # Batch mode
        batch = subparsers.add_parser('batch', 
            help='Run EML script in batch mode')
        batch.add_argument('script', help='Path to EML script file')
        
        # REST mode
        rest = subparsers.add_parser('rest',
            help='Start REST API server')
        rest.add_argument('--host', default='0.0.0.0',
            help='Host to bind to (default: 0.0.0.0)')
        rest.add_argument('--port', type=int, default=8000,
            help='Port to listen on (default: 8000)')

    def run(self, args: List[str] = None):
        args = self.parser.parse_args(args)
        
        if args.command == 'parse':
            self._run_parse(args.content)
        elif args.command == 'generate':
            self._run_generate(args.input)
        elif args.command == 'validate':
            self._run_validate(args.content)
        elif args.command == 'convert':
            self._run_convert(args)
        elif args.command == 'rest':
            self._run_rest(args.host, args.port)
        else:
            self.parser.print_help()

    def _run_parse(self, content: str):
        """Parse PEML content"""
        parser = PEMLParser()
        try:
            message = parser.parse(content)
            print("\nParsed message:")
            print(json.dumps(parser.to_dict(message), indent=2))
        except PEMLError as e:
            print(f"Error: {str(e)}")

    def _run_generate(self, args):
        """Generate PEML from JSON"""
        with open(args.input, 'r') as f:
            data = json.load(f)
            
        parser = PEMLParser()
        validator = PEMLValidator()
        
        if args.validate:
            validator.validate(data)
            
        message = parser.from_dict(data)
        print("\nGenerated PEML:")
        print(message.as_string())

    def _run_validate(self, content: str):
        """Validate PEML content"""
        parser = PEMLParser()
        validator = PEMLValidator()
        
        try:
            message = parser.parse(content)
            validator.validate(message)
            print("\nMessage is valid!")
        except (PEMLError, ValueError) as e:
            print(f"Error: {str(e)}")

    def _run_convert(self, args):
        """Convert between formats"""
        parser = PEMLParser()
        
        if args.from_format == 'peml':
            with open(args.input, 'r') as f:
                content = f.read()
            message = parser.parse(content)
            data = parser.to_dict(message)
            output = json.dumps(data, indent=2)
        else:  # from_format == 'json'
            with open(args.input, 'r') as f:
                data = json.load(f)
            message = parser.from_dict(data)
            output = message.as_string()
        
        if args.output:
            with open(args.output, 'w') as f:
                f.write(output)
        else:
            print(output)

    def _run_rest(self, host: str, port: int):
        """Start REST server"""
        from .api import app
        import uvicorn
        print(f"Starting PEML REST server on {host}:{port}")
        uvicorn.run(app, host=host, port=port)

    def _run_batch(self, script_path: str):
        print(f"Running EML script: {script_path}")
        # TODO: Implement batch script execution
        print("Batch execution completed")

    def _run_rest(self, host: str, port: int):
        print(f"Starting REST server on {host}:{port}")
        # TODO: Implement REST server
        print("REST server started")

if __name__ == '__main__':
    cli = EMLCLI()
    cli.run()
