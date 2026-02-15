import React, { useState } from 'react';
import { FileDown, Loader2 } from 'lucide-react';
import axios from 'axios';

const PdfExportButton = ({ data, filters }) => {
    const [isExporting, setIsExporting] = useState(false);
    const [error, setError] = useState(null);

    const handleExport = async () => {
        setIsExporting(true);
        setError(null);

        try {
            const response = await axios.post(
                '/api/export-pdf',
                {
                    data: data,
                    filters: filters
                },
                {
                    responseType: 'blob', // Important for binary data
                    timeout: 60000 // 60 second timeout for large datasets
                }
            );

            // Create download link
            const blob = new Blob([response.data], { type: 'application/pdf' });
            const url = window.URL.createObjectURL(blob);
            const link = document.createElement('a');
            link.href = url;
            link.download = `skills_matrix_${new Date().toISOString().split('T')[0]}.pdf`;
            document.body.appendChild(link);
            link.click();

            // Cleanup
            document.body.removeChild(link);
            window.URL.revokeObjectURL(url);

        } catch (err) {
            console.error('PDF export failed:', err);
            setError(err.response?.data?.detail || 'Failed to generate PDF. Please try again.');
        } finally {
            setIsExporting(false);
        }
    };

    return (
        <div className="relative">
            <button
                onClick={handleExport}
                disabled={isExporting || !data || data.length === 0}
                className={`
                    flex items-center gap-2 px-4 py-2 rounded-lg
                    font-medium text-sm transition-all shadow-sm
                    ${isExporting || !data || data.length === 0
                        ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                        : 'bg-blue-600 text-white hover:bg-blue-700 active:scale-95'
                    }
                `}
                title={data?.length === 0 ? 'No data to export' : 'Download as PDF'}
            >
                {isExporting ? (
                    <>
                        <Loader2 className="w-4 h-4 animate-spin" />
                        <span>Generating PDF...</span>
                    </>
                ) : (
                    <>
                        <FileDown className="w-4 h-4" />
                        <span>Export to PDF</span>
                    </>
                )}
            </button>

            {error && (
                <div className="absolute top-full mt-2 left-0 right-0 bg-red-50 border border-red-200 text-red-700 px-3 py-2 rounded-lg text-xs z-10 shadow-lg min-w-[200px]">
                    {error}
                </div>
            )}
        </div>
    );
};

export default PdfExportButton;
