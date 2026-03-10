import React, { useState } from 'react';
import { scrapeStore } from '../api/products';
import './SetupPanel.css';

interface SetupPanelProps {
    sessionId: string | null;
    onComplete: () => void;
}

const DEFAULT_LINKS = [
    { name: 'Kith', url: 'kith.com' },
    { name: 'Gymshark', url: 'gymshark.com' },
    { name: 'ColourPop', url: 'colourpop.com' },
    { name: 'Nomad Goods', url: 'nomadgoods.com' },
    { name: 'Brooklinen', url: 'brooklinen.com' },
];

export function SetupPanel({ sessionId, onComplete }: SetupPanelProps) {
    const [url, setUrl] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const handleScrape = async (targetUrl: string) => {
        if (!sessionId) {
            setError('Initializing session... please wait');
            return;
        }

        setIsLoading(true);
        setError(null);

        try {
            const success = await scrapeStore(sessionId, targetUrl);
            if (success) {
                onComplete();
            } else {
                setError('Failed to scrape products. Ensure the backend is running.');
                setIsLoading(false);
            }
        } catch (err) {
            setError('An error occurred during scraping.');
            setIsLoading(false);
        }
    };

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        if (url.trim()) {
            handleScrape(url.trim());
        }
    };

    return (
        <div className="setup-panel-container">
            <div className="setup-panel-card">
                <h1>Gen UI Storefront Demo</h1>
                <p className="setup-panel-subtitle">Select a store to analyze and inject into the demo, or enter your own Shopify URL.</p>

                {error && <div className="setup-panel-error">{error}</div>}

                {isLoading ? (
                    <div className="setup-panel-loading">
                        <div className="spinner"></div>
                        <p>Scraping products... This may take a few seconds.</p>
                    </div>
                ) : (
                    <>
                        <form onSubmit={handleSubmit} className="setup-panel-form">
                            <input
                                type="text"
                                placeholder="Enter Shopify URL (e.g. kith.com)"
                                value={url}
                                onChange={(e) => setUrl(e.target.value)}
                                className="setup-panel-input"
                            />
                            <button type="submit" className="setup-panel-button" disabled={!url.trim()}>
                                Scrape Custom URL
                            </button>
                        </form>

                        <div className="setup-panel-divider">
                            <span>OR</span>
                        </div>

                        <div className="setup-panel-defaults">
                            <h3>Try a default store:</h3>
                            <div className="default-links-grid">
                                {DEFAULT_LINKS.map((link) => (
                                    <button
                                        key={link.name}
                                        className="default-link-button"
                                        onClick={() => handleScrape(link.url)}
                                    >
                                        {link.name}
                                    </button>
                                ))}
                            </div>
                        </div>

                        <button className="setup-panel-skip" onClick={onComplete}>
                            Skip (Use Default Products)
                        </button>
                    </>
                )}
            </div>
        </div>
    );
}
