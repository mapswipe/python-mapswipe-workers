// NOTE: these may not be used
export const isDevelopment = process.env.NODE_ENV === 'development';
export const isProduction = process.env.NODE_ENV === 'production';
export const isTesting = process.env.NODE_ENV === 'test';

export const isBeta = process.env.REACT_APP_ENVIRONMENT === 'beta';
export const isAlpha = process.env.REACT_APP_ENVIRONMENT === 'alpha';
export const isNightly = process.env.REACT_APP_ENVIRONMENT === 'nightly';
export const isDev = !isBeta && !isAlpha && !isNightly;
