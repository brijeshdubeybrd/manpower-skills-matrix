import React, { useMemo, useState } from 'react';
import {
    useReactTable,
    getCoreRowModel,
    getSortedRowModel,
    flexRender,
    getFilteredRowModel,
} from '@tanstack/react-table';
import { ArrowUpDown, Trash2, Edit2, Save, X } from 'lucide-react';
import axios from 'axios';
import clsx from 'clsx';

const DataGrid = ({ data, setData, viewMode }) => {
    const [editingCell, setEditingCell] = useState(null); // { rowId, columnId, value }
    const [updateStatus, setUpdateStatus] = useState(null); // 'saving', 'success', 'error'

    const handleCellUpdate = async (rowId, columnId, newValue) => {
        // Optimistic update
        const rowIndex = data.findIndex(row => row.id === rowId);
        const oldRow = data[rowIndex];
        const newRow = { ...oldRow, [columnId]: newValue };

        const newData = [...data];
        newData[rowIndex] = newRow;
        setData(newData);

        setUpdateStatus('saving');
        try {
            await axios.put(`/api/manpower/${rowId}`, newRow);
            setUpdateStatus('success');
            setTimeout(() => setUpdateStatus(null), 2000);
        } catch (error) {
            console.error("Failed to update record", error);
            // Revert on failure
            const revertedData = [...data];
            revertedData[rowIndex] = oldRow;
            setData(revertedData);
            setUpdateStatus('error');
        }
        setEditingCell(null);
    };

    const handleDelete = async (rowId) => {
        if (window.confirm("Delete this record?")) {
            try {
                await axios.delete(`/api/manpower/${rowId}`);
                setData(prev => prev.filter(row => row.id !== rowId));
            } catch (error) {
                console.error("Failed to delete record", error);
            }
        }
    }

    const columns = useMemo(() => [
        {
            accessorKey: 'Function',
            header: ({ column }) => (
                <button variant="ghost" onClick={() => column.toggleSorting(column.getIsSorted() === 'asc')} className="flex items-center font-semibold">
                    Function
                    <ArrowUpDown className="ml-2 h-4 w-4" />
                </button>
            ),
            cell: info => <span className="font-medium text-gray-900">{info.getValue()}</span>,
        },

        {
            accessorKey: 'Skill_Name',
            header: 'Skill',
            cell: info => <span className="text-blue-700 font-medium">{info.getValue()}</span>
        },
        {
            accessorKey: 'Proficiency_Level',
            header: 'Proficiency',
            cell: ({ getValue, row, column: { id }, table }) => {
                const initialValue = getValue();
                const isEditing = editingCell?.rowId === row.original.id && editingCell?.columnId === id;

                if (isEditing) {
                    return (
                        <select
                            autoFocus
                            className="border border-blue-500 rounded px-1 py-0.5 text-sm w-full bg-white shadow-sm"
                            value={editingCell.value}
                            onChange={(e) => setEditingCell({ ...editingCell, value: e.target.value })}
                            onBlur={() => handleCellUpdate(row.original.id, id, editingCell.value)}
                            onKeyDown={(e) => {
                                if (e.key === 'Enter') handleCellUpdate(row.original.id, id, editingCell.value);
                                if (e.key === 'Escape') setEditingCell(null);
                            }}
                        >
                            {[1, 2, 3, 4, 5].map(lvl => (
                                <option key={lvl} value={lvl}>{lvl}</option>
                            ))}
                        </select>
                    )
                }

                return (
                    <div
                        className="cursor-pointer hover:bg-gray-100 px-2 py-1 rounded transition-colors flex items-center justify-between group"
                        onClick={() => setEditingCell({ rowId: row.original.id, columnId: id, value: initialValue })}
                    >
                        <span className={clsx(
                            "inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium",
                            initialValue >= 4 ? "bg-green-100 text-green-800" :
                                initialValue >= 3 ? "bg-yellow-100 text-yellow-800" :
                                    "bg-red-100 text-red-800"
                        )}>
                            {initialValue}
                        </span>
                        <Edit2 className="w-3 h-3 text-gray-400 opacity-0 group-hover:opacity-100 ml-2" />
                    </div>
                );
            },
        },
        {
            accessorKey: 'Band',
            header: 'Band',
            cell: info => (
                <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-gray-100 text-gray-800 border border-gray-200">
                    {info.getValue()}
                </span>
            )
        },
        {
            accessorKey: 'Job_Role_Name_without_concat',
            header: 'Job Role',
            cell: info => <span className="text-gray-600">{info.getValue()}</span>
        },
        {
            accessorKey: 'SBU',
            header: 'SBU',
        },
        {
            accessorKey: 'Group', // Hidden or less prominent
            header: 'Group',
            cell: info => <span className="text-gray-400 text-xs">{info.getValue()}</span>
        },
        // Admin Actions
        ...(viewMode === 'admin' ? [{
            id: 'actions',
            cell: ({ row }) => (
                <button
                    onClick={() => handleDelete(row.original.id)}
                    className="text-red-600 hover:text-red-900 p-1 rounded hover:bg-red-50"
                    title="Delete Record"
                >
                    <Trash2 className="h-4 w-4" />
                </button>
            ),
        }] : [])
    ], [viewMode, editingCell, data]);

    const table = useReactTable({
        data,
        columns,
        getCoreRowModel: getCoreRowModel(),
        getSortedRowModel: getSortedRowModel(),
        getFilteredRowModel: getFilteredRowModel(),
    });

    return (
        <div className="w-full">
            <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                        {table.getHeaderGroups().map(headerGroup => (
                            <tr key={headerGroup.id}>
                                {headerGroup.headers.map(header => (
                                    <th
                                        key={header.id}
                                        className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider sticky top-0 bg-gray-50 cursor-pointer hover:bg-gray-100 select-none"
                                        style={{ width: header.column.getSize() }}
                                        onClick={header.column.getToggleSortingHandler()}
                                    >
                                        {flexRender(header.column.columnDef.header, header.getContext())}
                                    </th>
                                ))}
                            </tr>
                        ))}
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                        {table.getRowModel().rows.map(row => (
                            <tr key={row.id} className="hover:bg-blue-50/50 transition-colors">
                                {row.getVisibleCells().map(cell => (
                                    <td key={cell.id} className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                        {flexRender(cell.column.columnDef.cell, cell.getContext())}
                                    </td>
                                ))}
                            </tr>
                        ))}
                        {data.length === 0 && (
                            <tr>
                                <td colSpan={columns.length} className="px-6 py-12 text-center text-gray-500">
                                    No records found matching your filters.
                                </td>
                            </tr>
                        )}
                    </tbody>
                </table>
            </div>
            {/* Simple Pagination or Footer could go here */}
            <div className="px-6 py-3 border-t border-gray-200 bg-gray-50 text-sm text-gray-500 flex justify-between items-center">
                <span>Showing {table.getRowModel().rows.length} records</span>
                {updateStatus === 'saving' && <span className="text-yellow-600 flex items-center"><span className="animate-pulse mr-2">●</span> Saving...</span>}
                {updateStatus === 'success' && <span className="text-green-600 flex items-center"><Save className="w-4 h-4 mr-1" /> Saved</span>}
                {updateStatus === 'error' && <span className="text-red-600 flex items-center"><X className="w-4 h-4 mr-1" /> Update failed</span>}
            </div>
        </div>
    );
};

export default DataGrid;
