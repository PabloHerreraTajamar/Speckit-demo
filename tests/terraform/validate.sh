#!/bin/bash
# Terraform Validation Script
#
# This script validates all Terraform files in the infrastructure directory.
# Run this before committing changes to ensure configuration is valid.

set -e

echo "=== Terraform Validation Script ==="
echo ""

# Change to infrastructure directory
cd "$(dirname "$0")/../../infrastructure"

echo "1. Checking Terraform formatting..."
if terraform fmt -check -recursive; then
    echo "✓ All files are properly formatted"
else
    echo "✗ Some files need formatting. Run: terraform fmt -recursive"
    exit 1
fi

echo ""
echo "2. Validating Terraform configuration..."
if terraform validate; then
    echo "✓ Configuration is valid"
else
    echo "✗ Configuration has errors"
    exit 1
fi

echo ""
echo "=== All validation checks passed! ==="
