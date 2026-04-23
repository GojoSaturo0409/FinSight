import { useState, useRef } from 'react';
import { UploadCloud, CheckCircle2, Loader2 } from 'lucide-react';
import { apiFetch } from '../api';

const CSVUpload = ({ onUploadComplete }: { onUploadComplete: () => void }) => {
    const [dragging, setDragging] = useState(false);
    const [file, setFile] = useState<File | null>(null);
    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState<null | string>(null);
    const fileInputRef = useRef<HTMLInputElement>(null);

    const handleDrag = (e: React.DragEvent) => {
        e.preventDefault();
        e.stopPropagation();
        if (e.type === 'dragenter' || e.type === 'dragover') setDragging(true);
        else if (e.type === 'dragleave') setDragging(false);
    };

    const handleDrop = (e: React.DragEvent) => {
        e.preventDefault();
        e.stopPropagation();
        setDragging(false);
        if (e.dataTransfer.files && e.dataTransfer.files[0]) {
            setFile(e.dataTransfer.files[0]);
        }
    };

    const handleUpload = async () => {
        if (!file) return;
        setLoading(true);
        const formData = new FormData();
        formData.append('file', file);
        try {
            const res = await apiFetch('/ingestion/upload-csv', {
                method: 'POST',
                body: formData
            });
            setResult(`Successfully imported ${res.imported_count} transactions.`);
            onUploadComplete();
        } catch {
            setResult('Error uploading file');
        } finally {
            setLoading(false);
            setFile(null);
        }
    };

    return (
        <div className="bg-neutral-900/50 border border-white/5 rounded-2xl p-6">
            <h3 className="text-lg font-bold mb-3">Upload CSV</h3>

            {!result ? (
                <div
                    onDragEnter={handleDrag} onDragLeave={handleDrag} onDragOver={handleDrag} onDrop={handleDrop}
                    onClick={() => fileInputRef.current?.click()}
                    className={`border-2 border-dashed rounded-xl p-6 flex flex-col items-center justify-center cursor-pointer transition-colors ${dragging ? 'border-indigo-400 bg-indigo-500/10' : 'border-white/10 hover:border-white/20'}`}
                >
                    <input type="file" ref={fileInputRef} className="hidden" accept=".csv" onChange={e => { if (e.target.files) setFile(e.target.files[0]); }} />
                    <UploadCloud size={32} className={file ? 'text-indigo-400' : 'text-neutral-500'} />
                    <p className="mt-2 text-sm text-center text-neutral-400">
                        {file ? file.name : 'Drag & drop bank CSV here or click to browse'}
                    </p>
                </div>
            ) : (
                <div className="bg-emerald-500/10 border border-emerald-500/20 rounded-xl p-4 flex items-center gap-3 text-emerald-400">
                    <CheckCircle2 size={24} />
                    <span className="text-sm font-medium">{result}</span>
                    <button onClick={() => setResult(null)} className="ml-auto text-xs underline">Upload another</button>
                </div>
            )}

            {file && !result && (
                <button onClick={handleUpload} disabled={loading} className="w-full mt-4 bg-white text-black font-semibold rounded-xl py-2 flex items-center justify-center gap-2">
                    {loading ? <Loader2 size={18} className="animate-spin" /> : 'Process File'}
                </button>
            )}
        </div>
    );
};
export default CSVUpload;
