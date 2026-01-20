#!/bin/bash
# Terraform Plan Test Script
# Validates Terraform configurations across all environments
# Usage: ./plan-test.sh [environment]
# If no environment specified, tests all environments (dev, staging, prod)

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Change to infrastructure directory
cd "$(dirname "$0")/../.." || exit 1

echo -e "${CYAN}=== Terraform Plan Validation ===${NC}\n"

# Function to test a single environment
test_environment() {
    local env=$1
    local tfvars_file="environments/${env}.tfvars"
    
    # Skip if tfvars file doesn't exist
    if [ ! -f "$tfvars_file" ]; then
        echo -e "${YELLOW}⚠️  Skipping ${env}: ${tfvars_file} not found${NC}"
        return 0
    fi
    
    echo -e "${CYAN}Testing environment: ${env}${NC}"
    echo "Using file: $tfvars_file"
    
    # Run terraform plan
    if terraform plan -var-file="$tfvars_file" -detailed-exitcode -no-color > /tmp/plan-${env}.txt 2>&1; then
        local exit_code=$?
        if [ $exit_code -eq 0 ]; then
            echo -e "${GREEN}✅ ${env}: No changes (infrastructure matches code)${NC}"
        elif [ $exit_code -eq 2 ]; then
            echo -e "${GREEN}✅ ${env}: Plan succeeded (changes detected)${NC}"
            # Show resource count
            local add_count=$(grep -c "will be created" /tmp/plan-${env}.txt || echo "0")
            local change_count=$(grep -c "will be updated" /tmp/plan-${env}.txt || echo "0")
            local destroy_count=$(grep -c "will be destroyed" /tmp/plan-${env}.txt || echo "0")
            echo "   Resources: +${add_count} ~${change_count} -${destroy_count}"
        fi
    else
        echo -e "${RED}❌ ${env}: Plan failed${NC}"
        echo "Error details:"
        tail -20 /tmp/plan-${env}.txt
        return 1
    fi
    
    # Verify expected naming conventions
    echo -n "   Checking naming conventions... "
    if grep -q "rg-${env}-taskmanager" /tmp/plan-${env}.txt; then
        echo -e "${GREEN}✅${NC}"
    else
        echo -e "${RED}❌ (Resource Group naming incorrect)${NC}"
        return 1
    fi
    
    # Verify environment tags
    echo -n "   Checking environment tags... "
    if grep -q "environment.*${env}" /tmp/plan-${env}.txt; then
        echo -e "${GREEN}✅${NC}"
    else
        echo -e "${RED}❌ (Environment tag missing)${NC}"
        return 1
    fi
    
    echo ""
}

# Main execution
if [ $# -eq 1 ]; then
    # Test single environment
    test_environment "$1"
else
    # Test all environments
    ENVIRONMENTS=("dev" "staging")
    
    # Add prod if prod.tfvars exists (not just .example)
    if [ -f "environments/prod.tfvars" ]; then
        ENVIRONMENTS+=("prod")
    fi
    
    all_passed=true
    for env in "${ENVIRONMENTS[@]}"; do
        if ! test_environment "$env"; then
            all_passed=false
        fi
    done
    
    echo -e "${CYAN}=== Validation Summary ===${NC}"
    if [ "$all_passed" = true ]; then
        echo -e "${GREEN}✅ All environments passed validation${NC}"
        exit 0
    else
        echo -e "${RED}❌ Some environments failed validation${NC}"
        exit 1
    fi
fi

# Cleanup
rm -f /tmp/plan-*.txt
