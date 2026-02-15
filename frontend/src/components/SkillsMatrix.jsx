import React, { useMemo, useState } from 'react';
import { Briefcase, Users, LayoutGrid, X } from 'lucide-react';

const SkillsMatrix = ({ data }) => {
    // State for view mode: 'all', 'functional', 'leadership'
    const [viewMode, setViewMode] = useState('all');
    // State for selected skill (for detail view)
    const [selectedSkill, setSelectedSkill] = useState(null);

    // 1. Group data by Band
    const matrixData = useMemo(() => {
        const grouped = {};
        // Updated Band Order based on Excel data
        const bandOrder = ['Band 1A', 'Band 1B', 'Band 2A', 'Band 2B', 'Band 3', 'Band 4', 'Band 5'];

        data.forEach(item => {
            const band = item.Band || 'Unassigned';
            if (!grouped[band]) {
                grouped[band] = { functional: [], leadership: [] };
            }

            const type = item.Competency_Type;
            const skillCard = {
                name: item.Skill_Name,
                definition: item.Skill_Definition,
                proficiency: item.Proficiency_Level, // Will be just the number after processing
                role: item.Job_Role_Name_without_concat,
                id: item.id || Math.random().toString(36).substr(2, 9) // Valid fallback ID
            };

            // Check for Leadership type (Excel value: "Raymond Leadership Competency")
            if (type === 'Behavioral' || type === 'Raymond Leadership Competency') {
                grouped[band].leadership.push(skillCard);
            } else {
                grouped[band].functional.push(skillCard);
            }
        });

        return Object.keys(grouped)
            .sort((a, b) => {
                const indexA = bandOrder.indexOf(a);
                const indexB = bandOrder.indexOf(b);
                if (indexA !== -1 && indexB !== -1) return indexA - indexB;
                if (indexA !== -1) return -1;
                if (indexB !== -1) return 1;
                return a.localeCompare(b);
            })
            .map(band => ({
                bandName: band,
                ...grouped[band]
            }));
    }, [data]);

    const handleClear = () => {
        setViewMode('all');
        setSelectedSkill(null);
    };

    const handleSkillClick = (skill) => {
        if (viewMode !== 'all') {
            setSelectedSkill(skill);
        }
    };

    if (!data || data.length === 0) {
        return (
            <div className="p-8 text-center text-gray-500 bg-white rounded-lg shadow-sm border border-gray-200 mt-4">
                No data available for the selected filters.
            </div>
        );
    }

    return (
        <div className="w-full space-y-4 mt-4">

            {/* Top Controls */}
            <div className="flex flex-wrap items-center gap-4 mb-6 p-4 bg-white rounded-lg shadow-sm border border-gray-200">
                <div className="text-sm font-medium text-gray-500 mr-2">View Mode:</div>

                <button
                    onClick={() => { setViewMode('functional'); setSelectedSkill(null); }}
                    className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors border
                        ${viewMode === 'functional'
                            ? 'bg-emerald-50 text-emerald-700 border-emerald-200 ring-2 ring-emerald-100'
                            : 'bg-white text-gray-600 border-gray-200 hover:bg-gray-50'}`}
                >
                    <Briefcase size={16} />
                    Functional Skills
                </button>

                <button
                    onClick={() => { setViewMode('leadership'); setSelectedSkill(null); }}
                    className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors border
                        ${viewMode === 'leadership'
                            ? 'bg-purple-50 text-purple-700 border-purple-200 ring-2 ring-purple-100'
                            : 'bg-white text-gray-600 border-gray-200 hover:bg-gray-50'}`}
                >
                    <Users size={16} />
                    Leadership Skills
                </button>

                {viewMode !== 'all' && (
                    <button
                        onClick={handleClear}
                        className="flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium text-gray-600 bg-gray-100 hover:bg-gray-200 hover:text-gray-900 transition-colors ml-auto"
                    >
                        <X size={16} />
                        Clear View
                    </button>
                )}
            </div>

            {/* Header Row */}
            <div className="hidden md:grid md:grid-cols-[100px_1fr_1fr] gap-4 px-4 py-3 rounded-t-lg text-sm font-bold text-white uppercase tracking-wider items-center text-center shadow-md" style={{ backgroundColor: '#CD202C' }}>
                <div>Band</div>
                <div>
                    {viewMode === 'leadership' ? 'Leadership Skills' : 'Functional Skills'}
                </div>
                <div>
                    {viewMode === 'all'
                        ? 'Leadership Skills'
                        : (selectedSkill ? 'Skill Details' : 'Select a Skill')}
                </div>
            </div>

            {/* Band Rows */}
            {matrixData.map((row) => (
                <div key={row.bandName} className="bg-white border border-gray-200 rounded-lg shadow-sm overflow-hidden flex flex-col md:grid md:grid-cols-[100px_1fr_1fr]">

                    {/* Band Label Column */}
                    <div className="bg-blue-50 p-4 flex items-center justify-center border-b md:border-b-0 md:border-r border-gray-200">
                        <div className="text-center">
                            <span className="text-2xl font-bold text-blue-800 block">{row.bandName}</span>
                            <span className="text-xs text-blue-600 font-medium uppercase tracking-wide">Band</span>
                        </div>
                    </div>

                    {/* Column 2: List (Variable content based on view mode) */}
                    <div className="p-0 border-b md:border-b-0 md:border-r border-gray-200 bg-white min-h-[150px]">
                        <h4 className="md:hidden text-xs font-bold text-white uppercase tracking-wider p-3 text-center" style={{ backgroundColor: '#CD202C' }}>
                            {viewMode === 'leadership' ? 'Leadership Skills' : 'Functional Skills'}
                        </h4>

                        <div className="flex flex-col">
                            {/* Logic: Show Functional if 'all' or 'functional'. Show Leadership if 'leadership'. */}
                            {((viewMode === 'all' || viewMode === 'functional') ? row.functional : row.leadership).length > 0 ? (
                                ((viewMode === 'all' || viewMode === 'functional') ? row.functional : row.leadership).map((skill, idx) => (
                                    <SkillRow
                                        key={`skill-${idx}`}
                                        skill={skill}
                                        type={(viewMode === 'leadership') ? 'leadership' : 'functional'}
                                        viewMode={viewMode}
                                        onClick={() => handleSkillClick(skill)}
                                        isSelected={selectedSkill === skill}
                                    />
                                ))
                            ) : (
                                <div className="text-gray-400 text-sm italic p-4 text-center">No skills defined.</div>
                            )}
                        </div>
                    </div>

                    {/* Column 3: Secondary List OR Detail View */}
                    <div className="p-0 bg-gray-50/30 min-h-[150px]">
                        <h4 className="md:hidden text-xs font-bold text-white uppercase tracking-wider p-3 text-center" style={{ backgroundColor: '#CD202C' }}>
                            {viewMode === 'all' ? 'Leadership Skills' : 'Skill Details'}
                        </h4>

                        {viewMode === 'all' ? (
                            // 'All' Mode: Show Leadership List
                            <div className="flex flex-col">
                                {row.leadership.length > 0 ? (
                                    row.leadership.map((skill, idx) => (
                                        <SkillRow key={`lead-${idx}`} skill={skill} type="leadership" viewMode={viewMode} />
                                    ))
                                ) : (
                                    <div className="text-gray-400 text-sm italic p-4 text-center">No leadership skills defined.</div>
                                )}
                            </div>
                        ) : (
                            // 'Functional/Leadership' Mode: Show Details
                            <div className="p-6 h-full flex flex-col justify-center">
                                {selectedSkill && ((viewMode === 'functional' && row.functional.includes(selectedSkill)) || (viewMode === 'leadership' && row.leadership.includes(selectedSkill))) ? (
                                    <div className="animate-fadeIn">
                                        <h3 className="text-lg font-bold text-gray-800 mb-2">{selectedSkill.name}</h3>
                                        <div className="mb-4">
                                            <span className={`
                                                text-xs uppercase font-bold px-2 py-1 rounded
                                                ${viewMode === 'leadership' ? 'bg-purple-100 text-purple-800' : 'bg-emerald-100 text-emerald-800'}
                                            `}>
                                                {viewMode === 'leadership' ? 'Leadership' : 'Functional'} Skill
                                            </span>
                                            <span className="ml-2 text-xs text-gray-500 font-medium">Proficiency Level: {selectedSkill.proficiency}/5</span>
                                        </div>
                                        <p className="text-gray-600 text-sm leading-relaxed">
                                            {selectedSkill.definition}
                                        </p>
                                    </div>
                                ) : (
                                    <div className="text-center text-gray-400 text-sm italic">
                                        {selectedSkill ? 'Select a skill in this band to view details.' : 'Click on a skill name to view its description.'}
                                    </div>
                                )}
                            </div>
                        )}
                    </div>

                </div>
            ))}
        </div>
    );
};

// Sub-component for individual skill rows
const SkillRow = ({ skill, type, viewMode, onClick, isSelected }) => {
    const isLeadership = type === 'leadership';
    const isCompact = viewMode !== 'all';

    return (
        <div
            onClick={isCompact ? onClick : undefined}
            className={`
        flex flex-col sm:flex-row gap-4 p-3 border-b last:border-b-0 text-sm transition-all
        ${isCompact ? 'cursor-pointer hover:bg-opacity-100' : 'hover:bg-opacity-50'}
        ${isSelected
                    ? (isLeadership ? 'bg-purple-100 border-purple-200' : 'bg-emerald-100 border-emerald-200')
                    : (isLeadership
                        ? 'border-purple-100 hover:bg-purple-50'
                        : 'border-emerald-100 hover:bg-emerald-50')
                }
      `}>
            {/* Left Side: Skill Name & Details */}
            <div className={`${isCompact ? 'w-full' : 'sm:w-2/5'} flex flex-col gap-2`}>
                <div className="flex items-center gap-3">
                    {/* Proficiency Number Badge */}
                    <div className={`
                    flex items-center justify-center w-8 h-8 rounded-full font-bold text-sm shrink-0 shadow-sm transition-colors
                    ${isSelected
                            ? (isLeadership ? 'bg-purple-600 text-white' : 'bg-emerald-600 text-white')
                            : (isLeadership ? 'bg-purple-100 text-purple-700' : 'bg-emerald-100 text-emerald-700')
                        }
                `}>
                        {skill.proficiency}
                    </div>

                    <div className="flex-1">
                        <h5 className={`font-semibold leading-tight mb-1 ${isSelected ? 'text-gray-900' : 'text-gray-800'}`}>
                            {skill.name}
                        </h5>
                        {/* Proficiency Dots - Show in all modes */}
                        <div className="flex items-center gap-1">
                            <div className="flex gap-1">
                                {[1, 2, 3, 4, 5].map(l => (
                                    <div
                                        key={l}
                                        className={`h-2.5 w-2.5 rounded-full ${l <= parseInt(skill.proficiency) ? (isLeadership ? 'bg-purple-400' : 'bg-emerald-400') : 'bg-gray-200'}`}
                                    />
                                ))}
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            {/* Right Side: Description (Only in 'all' mode) */}
            {!isCompact && (
                <div className="sm:w-3/5 text-gray-600 text-xs leading-relaxed flex items-center">
                    <p>{skill.definition}</p>
                </div>
            )}
        </div>
    );
};

export default SkillsMatrix;
