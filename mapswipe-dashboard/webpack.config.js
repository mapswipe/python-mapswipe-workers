const path = require('path');
const HtmlWebpackPlugin = require('html-webpack-plugin');
const MiniCssExtractPlugin = require('mini-css-extract-plugin');
const { HotModuleReplacementPlugin, EnvironmentPlugin } = require('webpack');
const Dotenv = require('dotenv-webpack');
const { GitRevisionPlugin } = require('git-revision-webpack-plugin');
const WebpackPwaManifest = require('webpack-pwa-manifest');
const { merge } = require('webpack-merge');
const CircularDependencyPlugin = require('circular-dependency-plugin');
const TerserPlugin = require('terser-webpack-plugin');
const CssMinimizerWebpackPlugin = require('css-minimizer-webpack-plugin');
const StyleLintPlugin = require('stylelint-webpack-plugin');
const ESLintPlugin = require('eslint-webpack-plugin');
const WorkboxWebpackPlugin = require('workbox-webpack-plugin');
const CompressionPlugin = require('compression-webpack-plugin');
const ResourceHintWebpackPlugin = require('resource-hints-webpack-plugin');
const ReactRefreshWebpackPlugin = require('@pmmmwh/react-refresh-webpack-plugin');

const pkg = require('./package.json');

function getPath(value) {
    return path.resolve(__dirname, value);
}

const gitRevisionPlugin = new GitRevisionPlugin();

const isProduction = process.env.NODE_ENV === 'production';

module.exports = () => {
    const config = {
        // TODO: define context
        mode: isProduction
            ? 'production'
            : 'development',
        devtool: isProduction
            ? 'source-map'
            : 'eval-cheap-source-map',
        entry: getPath('app/index.tsx'),
        node: false,
        resolve: {
            extensions: ['.js', '.jsx', '.ts', '.tsx'],
            symlinks: false,
        },
        output: {
            path: getPath('build/'),
            publicPath: '/',
            sourceMapFilename: '[file].map',
            chunkFilename: isProduction
                ? 'js/[name].[contenthash].chunk.js'
                : 'js/[name].chunk.js',
            filename: isProduction
                ? 'js/[name].[contenthash].bundle.js'
                : 'js/[name].bundle.js',
            assetModuleFilename: isProduction
                ? 'assets/[name].[contenthash][ext]'
                : 'assets/[name][ext]',
            clean: true,
        },
        module: {
            rules: [
                {
                    test: /\.[tj]sx?$/,
                    include: getPath('app/'),
                    exclude: /node_modules/,
                    loader: 'babel-loader',
                    options: {
                        plugins: [
                            !isProduction && require.resolve('react-refresh/babel'),
                        ].filter(Boolean),
                    },
                },
                {
                    test: /\.css$/,
                    include: getPath('app/'),
                    exclude: /node_modules/,
                    use: [
                        isProduction ? MiniCssExtractPlugin.loader : 'style-loader',
                        {
                            loader: 'css-loader',
                            options: {
                                importLoaders: 1,
                                modules: {
                                    localIdentName: '[name]_[local]_[hash:base64:5]',
                                    exportLocalsConvention: 'camelCaseOnly',
                                },
                                esModule: true,
                                sourceMap: true,
                            },
                        },
                        {
                            loader: 'postcss-loader',
                            ident: 'postcss',
                            options: {
                                sourceMap: true,
                            },
                        },
                    ],
                },
                {
                    test: /\.css$/,
                    include: getPath('node_modules/'),
                    use: [
                        isProduction ? MiniCssExtractPlugin.loader : 'style-loader',
                        'css-loader',
                    ],
                },
                {
                    test: /\.(eot|svg|ttf|woff|woff2|png|jpg|gif)$/i,
                    exclude: /(node_modules)/,
                    include: getPath('app/'),
                    type: 'asset/resource',
                    /*
                    options: {
                        name: isProduction
                            ? 'assets/[name].[contenthash]][ext]',
                            : 'assets/[name].[ext]',
                    },
                    */
                },
            ],
        },
        plugins: [
            new EnvironmentPlugin({
                MY_APP_ID: pkg.name,
                MY_APP_NAME: pkg.longName,
                // MY_APP_DESCRIPTION: pkg.description,

                REACT_APP_VERSION: gitRevisionPlugin.version(),
                REACT_APP_COMMITHASH: gitRevisionPlugin.commithash(),
                REACT_APP_BRANCH: gitRevisionPlugin.branch(),
            }),
            new Dotenv({
                safe: true,
                expand: true,
                allowEmptyValues: true,
                defaults: false,
                path: getPath('.env'),
                systemvars: !!isProduction, // NOTE: need to filter system variables
            }),
            new MiniCssExtractPlugin({
                filename: isProduction
                    ? 'css/[name].[contenthash].css'
                    : 'css/[name].css',
                chunkFilename: isProduction
                    ? 'css/[id].[contenthash].css'
                    : 'css/[id].css',
            }),
            new HtmlWebpackPlugin({
                favicon: getPath('app/favicon.ico'),
                template: getPath('app/index.html'),
                filename: 'index.html',
                title: pkg.name,
                meta: {
                    charset: 'UTF-8',
                    viewport: 'width=device-width, initial-scale=1.0',
                    description: pkg.description,
                    referrer: 'origin',
                },
            }),
            new WebpackPwaManifest({
                name: pkg.name,
                short_name: pkg.name,
                description: pkg.description,
                orientation: 'landscape',
                // background_color: '#f0f0f0',
                // theme_color: '#303f9f',
                display: 'standalone',
                start_url: '/',
                scope: '/',
                icons: [
                    {
                        src: getPath('app/favicon.png'),
                        sizes: [96, 128, 192, 256, 384, 512],
                        destination: 'icons',
                    },
                ],
            }),
            new CircularDependencyPlugin({
                exclude: /node_modules/,
                failOnError: false,
                allowAsyncCycles: false,
                cwd: __dirname,
            }),
            new StyleLintPlugin({
                files: ['**/*.css'],
                context: getPath('app/'),
            }),
            new ESLintPlugin({
                extensions: ['.js', '.jsx', '.ts', '.tsx'],
                reportUnusedDisableDirectives: 'warn',
            }),
        ],
    };

    if (isProduction) {
        return merge(
            config,
            {
                performance: {
                    hints: 'warning',
                },
                optimization: {
                    moduleIds: 'deterministic', // 'hashed',
                    runtimeChunk: 'single',
                    minimizer: [
                        // NOTE: Using TerserPlugin instead of UglifyJsPlugin
                        // as es6 support deprecated
                        new TerserPlugin({
                            parallel: true,
                            terserOptions: {
                                mangle: true,
                                compress: { typeofs: false },
                            },
                        }),
                        new CssMinimizerWebpackPlugin(),
                    ],
                    splitChunks: {
                        cacheGroups: {
                            defaultVendors: {
                                test: /[\\/]node_modules[\\/]/,
                                name: 'vendors',
                                chunks: 'all',
                                maxSize: 200 * 1024, // 200 KB
                            },
                        },
                    },
                },
                plugins: [
                    new ResourceHintWebpackPlugin(),
                    new CompressionPlugin(),
                    new WorkboxWebpackPlugin.GenerateSW({
                        // these options encourage the ServiceWorkers to get in there fast
                        // and not allow any straggling "old" SWs to hang around
                        cleanupOutdatedCaches: true,
                        clientsClaim: true,
                        skipWaiting: true,
                        include: [/\.html$/, /\.js$/, /\.css$/],
                        navigateFallback: '/index.html',
                        navigateFallbackDenylist: [/^\/icons/, /^\/assets/, /^\/api/, /^\/graphql/, /^\/graphiql/],
                        maximumFileSizeToCacheInBytes: 500 * 1024,
                        runtimeCaching: [
                            {
                                urlPattern: /assets/,
                                handler: 'StaleWhileRevalidate',
                            },
                        ],
                        exclude: [/\.map$/, /\.map.gz$/, /index.html/, /index.html.gz/],
                    }),
                ],
            },
        );
    }

    return merge(
        config,
        {
            devServer: {
                host: '0.0.0.0',
                port: 3080,
                overlay: true,
                hot: true,
                liveReload: false,
                historyApiFallback: true,
                watchContentBase: true,
                watchOptions: {
                    ignored: /node_modules/,
                },

                clientLogLevel: 'none',
                publicPath: '/',
            },
            plugins: [
                new HotModuleReplacementPlugin(),
                new ReactRefreshWebpackPlugin(),
            ],
            /*
            // TODO: enable this later
            experiments: {
                lazyCompilation: true,
            },
            */
        },
    );
};
