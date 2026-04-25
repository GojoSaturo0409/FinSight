import { useState, useCallback } from 'react';
import { usePlaidLink } from 'react-plaid-link';
import { apiFetch } from '../api';

interface PlaidLinkButtonProps {
    onSuccess?: () => void;
}

const PlaidLinkButton = ({ onSuccess }: PlaidLinkButtonProps) => {
    const [linkToken, setLinkToken] = useState<string | null>(null);
    const [loading, setLoading] = useState(false);

    const checkAndFetchLinkToken = async () => {
        setLoading(true);
        try {
            const data = await apiFetch('/ingestion/plaid/create_link_token', { method: 'POST' });
            if (data.link_token) {
                setLinkToken(data.link_token);
            }
        } catch (e) {
            console.error("Error creating link token:", e);
        } finally {
            setLoading(false);
        }
    };

    const handleOnSuccess = useCallback(async (public_token: string) => {
        try {
            await apiFetch('/ingestion/plaid/set_access_token', {
                method: 'POST',
                body: JSON.stringify({ public_token }),
            });
            await apiFetch('/budget/evaluate-auto', { method: 'POST' });
            if (onSuccess) onSuccess();
        } catch (e) {
            console.error("Error exchanging public token:", e);
        }
    }, [onSuccess]);

    const config: Parameters<typeof usePlaidLink>[0] = {
        token: linkToken!,
        onSuccess: handleOnSuccess,
    };

    const { open, ready } = usePlaidLink(config);

    if (linkToken === 'link-sandbox-mock-12345') {
        return (
            <button
                onClick={() => handleOnSuccess('mock-public-token-123')}
                className="bg-indigo-600 hover:bg-indigo-700 w-full py-3 rounded-lg font-medium transition-colors border border-indigo-400/30"
            >
                Simulate Direct Bank Login
            </button>
        );
    }

    if (linkToken) {
        return (
            <button
                onClick={() => open()}
                disabled={!ready}
                className="bg-indigo-600 hover:bg-indigo-700 w-full py-3 rounded-lg font-medium transition-colors"
            >
                Connect with Plaid (Sandbox)
            </button>
        );
    }

    return (
        <button
            onClick={checkAndFetchLinkToken}
            disabled={loading}
            className="bg-indigo-600 hover:bg-indigo-700 w-full py-3 rounded-lg font-medium transition-colors disabled:opacity-50"
        >
            {loading ? 'Initializing Plaid...' : 'Link Bank Account'}
        </button>
    );
};

export default PlaidLinkButton;
