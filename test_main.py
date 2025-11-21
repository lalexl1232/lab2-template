#!/usr/bin/env python3
"""
Root test runner for all services.
This file allows you to run tests from the project root.

Usage:
    # Test all services
    python3 test_main.py
    # OR
    ./test_main.py

    # Test specific service
    python3 test_main.py payment
    python3 test_main.py cars
    python3 test_main.py rental
    python3 test_main.py gateway
"""

import subprocess
import sys
from pathlib import Path

SERVICES = {
    "payment": "services/payment_service",
    "cars": "services/cars_service",
    "rental": "services/rental_service",
    "gateway": "services/gateway_service"
}


def run_tests(service_name, service_path):
    """Run tests for a specific service."""
    separator = "=" * 60
    print(f"\n{separator}")
    print(f"Testing {service_name.upper()} Service")
    print(f"{separator}\n")

    service_dir = Path(__file__).parent / service_path

    # Run pytest in the service directory
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "test_main.py", "-v"],
        cwd=service_dir,
        capture_output=False
    )

    return result.returncode == 0


def main():
    if len(sys.argv) > 1:
        # Test specific service
        service = sys.argv[1].lower()
        if service not in SERVICES:
            print(f"Error: Unknown service '{service}'")
            print(f"Available services: {', '.join(SERVICES.keys())}")
            sys.exit(1)

        success = run_tests(service, SERVICES[service])
        sys.exit(0 if success else 1)
    else:
        # Test all services
        print("Running tests for all services...")
        failed_services = []

        for service_name, service_path in SERVICES.items():
            success = run_tests(service_name, service_path)
            if not success:
                failed_services.append(service_name)

        # Summary
        separator = "=" * 60
        print(f"\n{separator}")
        print("Test Summary")
        print(separator)

        if not failed_services:
            print("✅ All services passed tests!")
            sys.exit(0)
        else:
            print("❌ Failed services:")
            for service in failed_services:
                print(f"  - {service}")
            sys.exit(1)


if __name__ == "__main__":
    main()
