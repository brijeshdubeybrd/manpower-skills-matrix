import React, { useState, useRef, useEffect } from 'react';
import { ChevronDown, Check, X } from 'lucide-react';

const MultiSelect = ({ label, options, selectedValues, onChange, className = "" }) => {
    const [isOpen, setIsOpen] = useState(false);
    const dropdownRef = useRef(null);

    // Close dropdown when clicking outside
    useEffect(() => {
        const handleClickOutside = (event) => {
            if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
                setIsOpen(false);
            }
        };

        document.addEventListener('mousedown', handleClickOutside);
        return () => {
            document.removeEventListener('mousedown', handleClickOutside);
        };
    }, []);

    const toggleOption = (value) => {
        const newSelected = selectedValues.includes(value)
            ? selectedValues.filter(v => v !== value)
            : [...selectedValues, value];
        onChange(newSelected);
    };

    const clearSelection = (e) => {
        e.stopPropagation();
        onChange([]);
    };

    const displayText = selectedValues.length === 0
        ? label
        : selectedValues.length === 1
            ? selectedValues[0]
            : `${selectedValues.length} selected`;

    return (
        <div className={`relative group ${className}`} ref={dropdownRef}>
            <button
                type="button"
                onClick={() => setIsOpen(!isOpen)}
                className={`
                    flex items-center justify-between w-full
                    appearance-none bg-white border border-gray-300 
                    text-gray-700 py-1.5 pl-3 pr-2 rounded-md text-sm 
                    focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 
                    shadow-sm min-w-[160px] cursor-pointer
                    ${selectedValues.length > 0 ? 'border-blue-300 bg-blue-50' : ''}
                `}
            >
                <div className="flex-1 truncate text-left mr-2">
                    {selectedValues.length > 0 && (
                        <span className="font-semibold text-blue-700">{label}: </span>
                    )}
                    <span className={selectedValues.length === 0 ? 'text-gray-500' : 'text-gray-900'}>
                        {selectedValues.length === 0 ? `All ${label}s` : displayText}
                    </span>
                </div>

                <div className="flex items-center">
                    {selectedValues.length > 0 && (
                        <div
                            onClick={clearSelection}
                            className="p-0.5 hover:bg-gray-200 rounded-full mr-1 text-gray-400 hover:text-gray-600 cursor-pointer"
                        >
                            <X className="h-3 w-3" />
                        </div>
                    )}
                    <ChevronDown className={`h-4 w-4 text-gray-500 transition-transform ${isOpen ? 'transform rotate-180' : ''}`} />
                </div>
            </button>

            {isOpen && (
                <div className="absolute z-50 mt-1 w-full min-w-[200px] bg-white shadow-lg max-h-60 rounded-md py-1 text-base ring-1 ring-black ring-opacity-5 overflow-auto focus:outline-none sm:text-sm">
                    {options.length === 0 ? (
                        <div className="py-2 px-4 text-gray-500 italic">No options available</div>
                    ) : (
                        options.map((option) => {
                            const isSelected = selectedValues.includes(option.value);
                            return (
                                <div
                                    key={option.value}
                                    onClick={() => toggleOption(option.value)}
                                    className={`
                                        cursor-pointer select-none relative py-2 pl-3 pr-9 hover:bg-blue-50 transition-colors
                                        ${isSelected ? 'bg-blue-50 text-blue-900' : 'text-gray-900'}
                                    `}
                                >
                                    <div className="flex items-center">
                                        <div className={`
                                            flex items-center justify-center h-4 w-4 rounded border mr-3
                                            ${isSelected ? 'bg-blue-600 border-blue-600' : 'border-gray-300 bg-white'}
                                        `}>
                                            {isSelected && <Check className="h-3 w-3 text-white" />}
                                        </div>
                                        <span className={`block truncate ${isSelected ? 'font-medium' : 'font-normal'}`}>
                                            {option.label}
                                        </span>
                                    </div>
                                    {option.count !== undefined && (
                                        <span className="absolute inset-y-0 right-0 flex items-center pr-4 text-gray-400 text-xs">
                                            {option.count}
                                        </span>
                                    )}
                                </div>
                            );
                        })
                    )}
                </div>
            )}
        </div>
    );
};

export default MultiSelect;
