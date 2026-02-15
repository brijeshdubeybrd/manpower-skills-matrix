import React, { useState, useMemo, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import axios from 'axios';
import DataGrid from './DataGrid';
import FilterBar from './FilterBar';
import SkillsMatrix from './SkillsMatrix'; // Import new component
import PdfExportButton from './PdfExportButton'; // Import PDF Export Button
import { LogOut, User, Database, LayoutGrid, Table as TableIcon } from 'lucide-react';

const Dashboard = () => {
    const { user, logout } = useAuth();
    const [data, setData] = useState([]);
    const [loading, setLoading] = useState(true);
    const [isAdminView, setIsAdminView] = useState(false);
    const [isMatrixView, setIsMatrixView] = useState(true); // Default to Matrix View as requested
    const [filters, setFilters] = useState({
        Function: [],
        Band: [],
        SBU: [],
        Role: []
    });

    useEffect(() => {
        fetchData();
    }, []);

    const fetchData = async () => {
        setLoading(true);
        try {
            const response = await axios.get('/api/manpower');
            setData(response.data);
        } catch (error) {
            console.error("Error fetching data:", error);
        } finally {
            setLoading(false);
        }
    };

    const handleReset = async () => {
        if (confirm('Are you sure you want to reset all data to default? This cannot be undone.')) {
            setLoading(true);
            try {
                await axios.post('/api/reset-data');
                await fetchData();
            } catch (error) {
                alert('Failed to reset data');
            } finally {
                setLoading(false);
            }
        }
    };

    const filteredData = useMemo(() => {
        return data.filter(item => {
            return (
                (filters.Function.length === 0 || filters.Function.includes(item.Function)) &&
                (filters.Band.length === 0 || filters.Band.includes(item.Band)) &&
                (filters.SBU.length === 0 || filters.SBU.includes(item.SBU)) &&
                (filters.Role.length === 0 || filters.Role.includes(item.Job_Role_Name_without_concat))
            );
        });
    }, [data, filters]);

    // Extract unique values for filters
    const filterOptions = useMemo(() => {
        const options = { functions: [], bands: [], sbus: [], roles: [] };
        if (data.length) {
            options.functions = [...new Set(data.map(d => d.Function))].sort();
            options.bands = [...new Set(data.map(d => d.Band))].sort();
            options.sbus = [...new Set(data.map(d => d.SBU))].sort();
            options.roles = [...new Set(data.map(d => d.Job_Role_Name_without_concat))].sort();
        }
        return options;
    }, [data]);

    // Calculate available options based on *other* active filters (Faceted search)
    const availableOptions = useMemo(() => {
        if (!data.length) return { functions: [], bands: [], sbus: [], roles: [] };

        const getUnique = (dataset, key) => [...new Set(dataset.map(item => item[key]))];

        // 1. Available Functions (start with all data, filter by Band, SBU, Role)
        const functionsData = data.filter(item =>
            (filters.Band.length === 0 || filters.Band.includes(item.Band)) &&
            (filters.SBU.length === 0 || filters.SBU.includes(item.SBU)) &&
            (filters.Role.length === 0 || filters.Role.includes(item.Job_Role_Name_without_concat))
        );

        // 2. Available Bands (filter by Function, SBU, Role)
        const bandsData = data.filter(item =>
            (filters.Function.length === 0 || filters.Function.includes(item.Function)) &&
            (filters.SBU.length === 0 || filters.SBU.includes(item.SBU)) &&
            (filters.Role.length === 0 || filters.Role.includes(item.Job_Role_Name_without_concat))
        );

        // 3. Available SBUs (filter by Function, Band, Role)
        const sbusData = data.filter(item =>
            (filters.Function.length === 0 || filters.Function.includes(item.Function)) &&
            (filters.Band.length === 0 || filters.Band.includes(item.Band)) &&
            (filters.Role.length === 0 || filters.Role.includes(item.Job_Role_Name_without_concat))
        );

        // 4. Available Roles (filter by Function, Band, SBU)
        const rolesData = data.filter(item =>
            (filters.Function.length === 0 || filters.Function.includes(item.Function)) &&
            (filters.Band.length === 0 || filters.Band.includes(item.Band)) &&
            (filters.SBU.length === 0 || filters.SBU.includes(item.SBU))
        );

        return {
            functions: getUnique(functionsData, 'Function'),
            bands: getUnique(bandsData, 'Band'),
            sbus: getUnique(sbusData, 'SBU'),
            roles: getUnique(rolesData, 'Job_Role_Name_without_concat')
        };
    }, [data, filters]);


    return (
        <div className="min-h-screen bg-gray-50 flex flex-col">
            {/* Header */}
            <header className="bg-white shadow-sm z-10">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex justify-between items-center">
                    <div className="flex items-center gap-2">
                        <div className="bg-blue-600 p-2 rounded-lg">
                            <Database className="w-6 h-6 text-white" />
                        </div>
                        <h1 className="text-xl font-bold text-gray-900 tracking-tight">Manpower & Skills Matrix</h1>
                    </div>

                    <div className="flex items-center gap-4">
                        {/* View Toggles */}
                        <div className="bg-gray-100 p-1 rounded-lg flex items-center">
                            <button
                                onClick={() => setIsMatrixView(true)}
                                className={`p-1.5 rounded-md transition-all ${isMatrixView ? 'bg-white shadow text-blue-600' : 'text-gray-500 hover:text-gray-700'}`}
                                title="Skills Matrix View"
                            >
                                <LayoutGrid size={18} />
                            </button>
                            <button
                                onClick={() => setIsMatrixView(false)}
                                className={`p-1.5 rounded-md transition-all ${!isMatrixView ? 'bg-white shadow text-blue-600' : 'text-gray-500 hover:text-gray-700'}`}
                                title="Table View"
                            >
                                <TableIcon size={18} />
                            </button>
                        </div>

                        <div className="h-6 w-px bg-gray-200 mx-2"></div>

                        <div className="flex items-center gap-2 text-sm text-gray-600">
                            <User size={16} />
                            <span className="hidden sm:inline">{user?.email || 'Guest'}</span>
                        </div>
                        <button
                            onClick={logout}
                            className="text-gray-500 hover:text-red-600 transition-colors p-2 rounded-full hover:bg-red-50"
                            title="Sign Out"
                        >
                            <LogOut size={18} />
                        </button>
                    </div>
                </div>
            </header>

            {/* Filter Bar */}
            <FilterBar
                filters={filters}
                setFilters={setFilters}
                uniqueValues={filterOptions}
                availableOptions={availableOptions}
            />

            {/* Main Content */}
            <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6">

                {/* Actions Bar */}
                <div className="flex justify-between items-center mb-6">
                    <h2 className="text-lg font-semibold text-gray-800">
                        {isMatrixView ? 'Competency Matrix' : 'Employee Records'}
                        <span className="ml-2 text-sm font-normal text-gray-500 bg-gray-100 px-2 py-0.5 rounded-full">
                            {filteredData.length} records
                        </span>
                    </h2>

                    <div className="flex gap-3">
                        <PdfExportButton
                            data={filteredData}
                            filters={filters}
                        />
                        {!isMatrixView && (
                            <button
                                onClick={() => setIsAdminView(!isAdminView)}
                                className={`text-sm px-4 py-2 rounded-lg border transition-colors ${isAdminView ? 'bg-purple-50 border-purple-200 text-purple-700' : 'bg-white border-gray-200 text-gray-600 hover:bg-gray-50'}`}
                            >
                                {isAdminView ? 'Admin Mode On' : 'Switch to Admin View'}
                            </button>
                        )}

                        <button
                            onClick={handleReset}
                            className="text-sm px-4 py-2 bg-white border border-gray-200 text-gray-700 rounded-lg hover:bg-gray-50 hover:text-red-600 transition-colors shadow-sm"
                        >
                            Reset Data
                        </button>
                    </div>
                </div>

                {/* Content Area */}
                <div className="bg-white rounded-xl shadow-sm border border-gray-200 min-h-[500px]">
                    {loading ? (
                        <div className="flex items-center justify-center h-64">
                            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                        </div>
                    ) : (
                        <>
                            {isMatrixView ? (
                                <div className="p-4">
                                    <SkillsMatrix data={filteredData} />
                                </div>
                            ) : (
                                <DataGrid
                                    data={filteredData}
                                    isAdmin={isAdminView}
                                    onDataChange={fetchData} // Refresh after edit/delete
                                />
                            )}
                        </>
                    )}
                </div>

            </main>
        </div>
    );
};

export default Dashboard;
