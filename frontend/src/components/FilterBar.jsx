import React from 'react';
import { Filter } from 'lucide-react';
import MultiSelect from './MultiSelect';

const FilterBar = ({ filters, setFilters, uniqueValues, availableOptions = { functions: [], bands: [], sbus: [], roles: [] } }) => {

    const handleChange = (key, value) => {
        setFilters(prev => ({ ...prev, [key]: value }));
    };

    // Helper to format options
    const formatOptions = (values) => {
        return values.map(v => ({
            value: v,
            label: v
        }));
    };

    const sbuOptions = formatOptions(uniqueValues.sbus.sort());
    const functionOptions = formatOptions(uniqueValues.functions); // Already sorted in Dashboard
    const bandOptions = formatOptions(uniqueValues.bands.sort());
    const roleOptions = formatOptions(uniqueValues.roles.sort());

    const hasActiveFilters =
        (filters.Function && filters.Function.length > 0) ||
        (filters.Band && filters.Band.length > 0) ||
        (filters.SBU && filters.SBU.length > 0) ||
        (filters.Role && filters.Role.length > 0);

    return (
        <div className="flex flex-wrap gap-2 items-center pb-2 md:pb-0">
            <div className="flex items-center text-gray-500 mr-2">
                <Filter className="w-4 h-4 mr-1" />
                <span className="text-sm font-medium">Filters:</span>
            </div>

            {/* SBU Filter */}
            <MultiSelect
                label="SBU"
                options={sbuOptions}
                selectedValues={filters.SBU || []} // Ensure array
                onChange={(vals) => handleChange('SBU', vals)}
            />

            {/* Function Filter */}
            <MultiSelect
                label="Function"
                options={functionOptions}
                selectedValues={filters.Function || []}
                onChange={(vals) => handleChange('Function', vals)}
            />

            {/* Band Filter */}
            <MultiSelect
                label="Band"
                options={bandOptions}
                selectedValues={filters.Band || []}
                onChange={(vals) => handleChange('Band', vals)}
            />

            {/* Role Filter */}
            <MultiSelect
                label="Role"
                options={roleOptions}
                selectedValues={filters.Role || []}
                onChange={(vals) => handleChange('Role', vals)}
            />

            {hasActiveFilters && (
                <button
                    onClick={() => setFilters({ Function: [], Band: [], SBU: [], Role: [] })}
                    className="text-sm text-red-600 hover:text-red-800 ml-2 font-medium whitespace-nowrap"
                >
                    Clear All
                </button>
            )}
        </div>
    );
};

export default FilterBar;
