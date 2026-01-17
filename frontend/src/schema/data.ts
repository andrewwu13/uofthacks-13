/**
 * Product Data - Placeholder products for the storefront
 * 
 * Each product has realistic data to demonstrate the UI
 */

import type { ProductData } from './types';

// Placeholder images using picsum.photos (reliable, no API key needed)
const getProductImage = (seed: number) =>
    `https://picsum.photos/seed/${seed}/400/400`;

export const PRODUCTS: ProductData[] = [
    {
        id: 'prod_001',
        title: 'Wireless Noise-Canceling Headphones',
        description: 'Premium audio with 30-hour battery life and active noise cancellation.',
        price: 299.99,
        currency: 'USD',
        imageUrl: getProductImage(101),
        vendor: 'AudioTech',
        category: 'Electronics'
    },
    {
        id: 'prod_002',
        title: 'Merino Wool Sneakers',
        description: 'Sustainable comfort made from ZQ merino wool. Machine washable.',
        price: 98.00,
        currency: 'USD',
        imageUrl: getProductImage(102),
        vendor: 'EcoStep',
        category: 'Footwear'
    },
    {
        id: 'prod_003',
        title: 'Smart Fitness Watch',
        description: 'Track your health with heart rate, sleep, and GPS built-in.',
        price: 199.00,
        currency: 'USD',
        imageUrl: getProductImage(103),
        vendor: 'FitGear',
        category: 'Wearables'
    },
    {
        id: 'prod_004',
        title: 'Organic Cotton T-Shirt',
        description: 'Ultra-soft tee made from 100% organic cotton. Fair trade certified.',
        price: 45.00,
        currency: 'USD',
        imageUrl: getProductImage(104),
        vendor: 'GreenThread',
        category: 'Apparel'
    },
    {
        id: 'prod_005',
        title: 'Minimalist Leather Wallet',
        description: 'Slim design holds 8 cards and cash. Full-grain leather.',
        price: 79.00,
        currency: 'USD',
        imageUrl: getProductImage(105),
        vendor: 'CraftCo',
        category: 'Accessories'
    },
    {
        id: 'prod_006',
        title: 'Ceramic Pour-Over Coffee Set',
        description: 'Hand-crafted pour-over dripper with matching carafe and cups.',
        price: 125.00,
        currency: 'USD',
        imageUrl: getProductImage(106),
        vendor: 'BrewCraft',
        category: 'Home'
    },
    {
        id: 'prod_007',
        title: 'Bamboo Standing Desk',
        description: 'Electric height-adjustable desk with sustainable bamboo top.',
        price: 549.00,
        currency: 'USD',
        imageUrl: getProductImage(107),
        vendor: 'WorkWell',
        category: 'Furniture'
    },
    {
        id: 'prod_008',
        title: 'Titanium Water Bottle',
        description: 'Ultralight 750ml bottle. Keeps drinks cold 24h or hot 12h.',
        price: 65.00,
        currency: 'USD',
        imageUrl: getProductImage(108),
        vendor: 'HydroGear',
        category: 'Outdoor'
    },
    {
        id: 'prod_009',
        title: 'Wireless Charging Pad',
        description: 'Fast 15W charging for all Qi-enabled devices. Sleek aluminum design.',
        price: 49.00,
        currency: 'USD',
        imageUrl: getProductImage(109),
        vendor: 'PowerUp',
        category: 'Electronics'
    },
    {
        id: 'prod_010',
        title: 'Japanese Denim Jacket',
        description: 'Selvedge denim from Okayama. Raw indigo with copper buttons.',
        price: 285.00,
        currency: 'USD',
        imageUrl: getProductImage(110),
        vendor: 'DenimLab',
        category: 'Apparel'
    },
    {
        id: 'prod_011',
        title: 'Smart Home Hub',
        description: 'Control all your devices. Works with Alexa, Google, and HomeKit.',
        price: 129.00,
        currency: 'USD',
        imageUrl: getProductImage(111),
        vendor: 'HomeTech',
        category: 'Electronics'
    },
    {
        id: 'prod_012',
        title: 'Yoga Mat Pro',
        description: 'Extra thick cushioning with alignment markers. Non-slip grip.',
        price: 89.00,
        currency: 'USD',
        imageUrl: getProductImage(112),
        vendor: 'ZenFit',
        category: 'Fitness'
    }
];

// ============================================
// CONTENT DATA FOR OTHER MODULE TYPES
// ============================================

export interface HeroContent {
    headline: string;
    subtext: string;
    ctaText: string;
}

export const HERO_CONTENT: HeroContent[] = [
    {
        headline: 'Designed for Tomorrow',
        subtext: 'Discover products that push the boundaries of innovation and sustainability.',
        ctaText: 'Shop Now'
    },
    {
        headline: 'Less is More',
        subtext: 'Curated essentials for the modern minimalist lifestyle.',
        ctaText: 'Explore'
    },
    {
        headline: 'BREAK THE RULES',
        subtext: 'Bold design. Unapologetic style. Make a statement.',
        ctaText: 'See Collection'
    }
];

export interface BannerContent {
    text: string;
    highlight: string;
    icon?: string;
}

export const BANNER_CONTENT: BannerContent[] = [
    { text: 'Free shipping on orders over', highlight: '$50', icon: '🚚' },
    { text: 'New arrivals:', highlight: 'Spring Collection', icon: '✨' },
    { text: 'Limited time:', highlight: '20% OFF', icon: '🔥' },
    { text: 'Sustainable packaging:', highlight: '100% recyclable', icon: '♻️' }
];

export interface FeatureItem {
    icon: string;
    title: string;
    description: string;
}

export const FEATURE_CONTENT: FeatureItem[][] = [
    [
        { icon: '🚀', title: 'Fast Shipping', description: '2-day delivery on all orders' },
        { icon: '🔒', title: 'Secure Checkout', description: 'Your data is always protected' },
        { icon: '💬', title: '24/7 Support', description: 'We\'re here whenever you need us' }
    ],
    [
        { icon: '🌱', title: 'Sustainable', description: 'Eco-friendly materials and practices' },
        { icon: '✅', title: 'Quality Guaranteed', description: 'Lifetime warranty on all products' },
        { icon: '🎁', title: 'Gift Wrapping', description: 'Free gift packaging available' }
    ]
];

export interface TestimonialContent {
    quote: string;
    author: string;
    role: string;
    avatarSeed: number;
}

export const TESTIMONIAL_CONTENT: TestimonialContent[] = [
    {
        quote: 'The quality exceeded my expectations. This is my new go-to store.',
        author: 'Sarah Chen',
        role: 'Verified Buyer',
        avatarSeed: 201
    },
    {
        quote: 'Fast shipping and beautiful packaging. A premium experience from start to finish.',
        author: 'Marcus Johnson',
        role: 'VIP Member',
        avatarSeed: 202
    },
    {
        quote: 'Finally, a brand that cares about sustainability without compromising on style.',
        author: 'Elena Rodriguez',
        role: 'Eco Advocate',
        avatarSeed: 203
    }
];

export interface CTAContent {
    headline: string;
    subtext: string;
    buttonText: string;
}

export const CTA_CONTENT: CTAContent[] = [
    {
        headline: 'Join Our Newsletter',
        subtext: 'Get 15% off your first order plus exclusive early access.',
        buttonText: 'Subscribe'
    },
    {
        headline: 'Ready to Start?',
        subtext: 'Create an account and unlock member-only benefits.',
        buttonText: 'Sign Up Free'
    },
    {
        headline: 'LIMITED OFFER',
        subtext: 'Sale ends in 24 hours. Don\'t miss out.',
        buttonText: 'Shop Sale'
    }
];

// ============================================
// RANDOM DATA GETTERS
// ============================================

export function getRandomProduct(): ProductData {
    return PRODUCTS[Math.floor(Math.random() * PRODUCTS.length)];
}

export function getRandomHero(): HeroContent {
    return HERO_CONTENT[Math.floor(Math.random() * HERO_CONTENT.length)];
}

export function getRandomBanner(): BannerContent {
    return BANNER_CONTENT[Math.floor(Math.random() * BANNER_CONTENT.length)];
}

export function getRandomFeatures(): FeatureItem[] {
    return FEATURE_CONTENT[Math.floor(Math.random() * FEATURE_CONTENT.length)];
}

export function getRandomTestimonial(): TestimonialContent {
    return TESTIMONIAL_CONTENT[Math.floor(Math.random() * TESTIMONIAL_CONTENT.length)];
}

export function getRandomCTA(): CTAContent {
    return CTA_CONTENT[Math.floor(Math.random() * CTA_CONTENT.length)];
}
