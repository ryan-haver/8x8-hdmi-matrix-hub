#!/usr/bin/env node

/**
 * NounProject Icon Tool - CLI
 * Search and download icons from The Noun Project via Shaper Studio API
 */

import { Command } from 'commander';
import chalk from 'chalk';
import ora from 'ora';
import { ApiClient, ProxyPool, DownloadQueue, Catalog } from '../lib/index.js';
import fs from 'fs/promises';
import path from 'path';

const program = new Command();

// Shared state
let catalog = null;
let proxyPool = null;

/**
 * Initialize catalog and proxy pool from config
 */
async function init() {
  const configPath = path.join(process.cwd(), 'config', 'settings.json');
  
  // Initialize catalog (async for sql.js)
  catalog = new Catalog();
  await catalog.init();
  
  // Load proxy config if exists
  try {
    const configData = await fs.readFile(configPath, 'utf8');
    const config = JSON.parse(configData);
    
    if (config.proxy?.enabled) {
      proxyPool = new ProxyPool({ strategy: config.proxy.strategy || 'round-robin' });
      
      if (config.proxy.pia?.username) {
        proxyPool.addPIA(
          config.proxy.pia.username,
          config.proxy.pia.password,
          config.proxy.pia.servers
        );
      }
      
      if (config.proxy.custom?.length) {
        proxyPool.addAll(config.proxy.custom);
      }
    }
  } catch {
    // No config file, that's fine
  }
}

// Configure CLI
program
  .name('npicon')
  .description('Search and download icons from The Noun Project')
  .version('1.0.0');

/**
 * SEARCH command
 */
program
  .command('search <query>')
  .description('Search for icons')
  .option('-l, --limit <number>', 'Number of results', '20')
  .option('-s, --style <style>', 'Filter by style (line, solid)')
  .option('--json', 'Output as JSON')
  .option('--save', 'Save results to catalog')
  .action(async (query, options) => {
    await init();
    
    const spinner = ora(`Searching for "${query}"...`).start();
    
    try {
      const client = new ApiClient({ proxyPool });
      const result = await client.search(query, { limit: parseInt(options.limit) });
      
      spinner.succeed(`Found ${result.total} icons`);
      
      // Filter by style if specified
      let icons = result.icons;
      if (options.style) {
        icons = icons.filter(icon => 
          icon.styles?.some(s => s.style === options.style)
        );
      }
      
      // Save to catalog if requested
      if (options.save) {
        catalog.saveIcons(icons, query);
        catalog.logSearch(query, result.total, icons.length);
        console.log(chalk.green(`\n✓ Saved ${icons.length} icons to catalog`));
      }
      
      // Output
      if (options.json) {
        console.log(JSON.stringify(icons, null, 2));
      } else {
        console.log('');
        for (const icon of icons) {
          const styles = icon.styles?.map(s => s.style).join(', ') || 'unknown';
          console.log(
            chalk.cyan(icon.id.padEnd(10)),
            chalk.white(icon.term?.substring(0, 30).padEnd(32)),
            chalk.dim(`[${styles}]`),
            chalk.gray(`by ${icon.creator?.name || 'Unknown'}`)
          );
        }
        console.log('');
        console.log(chalk.dim(`Usage: ${result.usage?.usage || '?'}/${result.usage?.limit || '?'} this month`));
      }
      
    } catch (error) {
      spinner.fail(`Search failed: ${error.message}`);
      process.exit(1);
    }
    
    catalog.close();
  });

/**
 * DOWNLOAD command
 */
program
  .command('download')
  .description('Download icons')
  .option('-i, --ids <ids>', 'Comma-separated icon IDs to download')
  .option('-q, --query <query>', 'Search query to download results from')
  .option('-l, --limit <number>', 'Limit icons when using --query', '50')
  .option('-o, --output <dir>', 'Output directory', './icons')
  .option('-c, --concurrency <number>', 'Concurrent downloads', '3')
  .action(async (options) => {
    await init();
    
    if (!options.ids && !options.query) {
      console.error(chalk.red('Error: Must specify --ids or --query'));
      process.exit(1);
    }
    
    const client = new ApiClient({ proxyPool });
    const queue = new DownloadQueue(client, {
      outputDir: options.output,
      concurrency: parseInt(options.concurrency)
    });
    
    await queue.setOutputDir(options.output);
    
    let icons = [];
    
    // Get icons by IDs
    if (options.ids) {
      const ids = options.ids.split(',').map(id => id.trim());
      const spinner = ora(`Fetching metadata for ${ids.length} icons...`).start();
      
      // Check catalog first
      for (const id of ids) {
        const cached = catalog.getIcon(id);
        if (cached) {
          // Need to get fresh URL from API since signed URLs expire
          const result = await client.search(cached.term, { limit: 100 });
          const fresh = result.icons.find(i => i.id === id);
          if (fresh) icons.push(fresh);
        }
      }
      
      spinner.succeed(`Found ${icons.length} icons`);
    }
    
    // Get icons by query
    if (options.query) {
      const spinner = ora(`Searching for "${options.query}"...`).start();
      const result = await client.search(options.query, { limit: parseInt(options.limit) });
      icons = result.icons;
      spinner.succeed(`Found ${icons.length} icons`);
      
      // Save to catalog
      catalog.saveIcons(icons, options.query);
    }
    
    if (icons.length === 0) {
      console.log(chalk.yellow('No icons to download'));
      catalog.close();
      return;
    }
    
    // Set up progress display
    const downloadSpinner = ora('Starting downloads...').start();
    
    queue.on('progress', (progress) => {
      downloadSpinner.text = `Downloading: ${progress.done}/${progress.total} (${progress.percent}%) - ${progress.failed} failed`;
    });
    
    queue.on('completed', ({ icon }) => {
      catalog.markDownloaded(icon.id);
    });
    
    // Add icons to queue
    await queue.addAll(icons);
    
    // Wait for completion
    const stats = await queue.waitForAll();
    
    downloadSpinner.succeed(
      `Download complete: ${stats.completed} saved, ${stats.skipped} skipped, ${stats.failed} failed`
    );
    
    if (stats.failed > 0) {
      console.log(chalk.yellow('\nFailed downloads:'));
      for (const failure of queue.getFailures()) {
        console.log(chalk.red(`  - ${failure.icon.id}: ${failure.error}`));
      }
    }
    
    catalog.close();
  });

/**
 * SCRAPE command - bulk scrape by search terms
 */
program
  .command('scrape')
  .description('Bulk scrape icons by search terms')
  .option('-t, --terms <terms>', 'Comma-separated search terms', 'tv,gaming,hdmi')
  .option('-l, --limit <number>', 'Icons per term', '50')
  .option('-o, --output <dir>', 'Output directory', './icons')
  .option('--download', 'Also download SVGs')
  .option('--style <style>', 'Filter by style (line, solid)')
  .action(async (options) => {
    await init();
    
    const terms = options.terms.split(',').map(t => t.trim());
    const limit = parseInt(options.limit);
    
    console.log(chalk.cyan('\n📦 NounProject Bulk Scraper'));
    console.log(chalk.dim(`Terms: ${terms.join(', ')}`));
    console.log(chalk.dim(`Limit per term: ${limit}`));
    console.log('');
    
    const client = new ApiClient({ proxyPool });
    let allIcons = [];
    
    for (const term of terms) {
      const spinner = ora(`Searching: ${term}`).start();
      
      try {
        const result = await client.search(term, { limit });
        let icons = result.icons;
        
        // Filter by style
        if (options.style) {
          icons = icons.filter(icon => 
            icon.styles?.some(s => s.style === options.style)
          );
        }
        
        catalog.saveIcons(icons, term);
        catalog.logSearch(term, result.total, icons.length);
        allIcons.push(...icons);
        
        spinner.succeed(`${term}: ${icons.length} icons (${result.total} total available)`);
        
        // Rate limit between searches
        await new Promise(r => setTimeout(r, 500));
        
      } catch (error) {
        spinner.fail(`${term}: ${error.message}`);
      }
    }
    
    // Deduplicate
    const uniqueIcons = [...new Map(allIcons.map(i => [i.id, i])).values()];
    console.log(chalk.green(`\n✓ Total unique icons: ${uniqueIcons.length}`));
    
    // Download if requested
    if (options.download && uniqueIcons.length > 0) {
      console.log(chalk.cyan(`\n📥 Downloading ${uniqueIcons.length} SVGs...`));
      
      const queue = new DownloadQueue(client, { outputDir: options.output });
      await queue.setOutputDir(options.output);
      
      const downloadSpinner = ora('Starting...').start();
      
      queue.on('progress', (p) => {
        downloadSpinner.text = `${p.done}/${p.total} (${p.percent}%)`;
      });
      
      queue.on('completed', ({ icon }) => catalog.markDownloaded(icon.id));
      
      await queue.addAll(uniqueIcons);
      const stats = await queue.waitForAll();
      
      downloadSpinner.succeed(`Downloaded: ${stats.completed}, Skipped: ${stats.skipped}, Failed: ${stats.failed}`);
    }
    
    catalog.close();
  });

/**
 * STATS command
 */
program
  .command('stats')
  .description('Show catalog and API statistics')
  .action(async () => {
    await init();
    
    // Catalog stats
    const stats = catalog.getStats();
    console.log(chalk.cyan('\n📊 Catalog Statistics'));
    console.log(`  Total icons: ${chalk.white(stats.totalIcons)}`);
    console.log(`  Downloaded: ${chalk.green(stats.downloadedIcons)}`);
    console.log(`  Searches: ${chalk.white(stats.totalSearches)}`);
    
    if (stats.topTerms.length > 0) {
      console.log('\n  Top terms:');
      for (const term of stats.topTerms.slice(0, 5)) {
        console.log(`    ${chalk.cyan(term.term)}: ${term.count}`);
      }
    }
    
    // API usage
    console.log(chalk.cyan('\n🌐 API Usage'));
    try {
      const client = new ApiClient({ proxyPool });
      const usage = await client.getUsage();
      const percent = ((usage.usage / usage.limit) * 100).toFixed(1);
      console.log(`  Used: ${chalk.white(usage.usage)} / ${usage.limit} (${percent}%)`);
      console.log(`  Remaining: ${chalk.green(usage.limit - usage.usage)}`);
    } catch (error) {
      console.log(`  ${chalk.red('Could not fetch: ' + error.message)}`);
    }
    
    // Proxy stats
    if (proxyPool && proxyPool.hasProxies()) {
      console.log(chalk.cyan('\n🔄 Proxy Pool'));
      console.log(`  Proxies: ${proxyPool.count}`);
      console.log(`  Strategy: ${proxyPool.strategy}`);
      const proxyStats = proxyPool.getStats();
      for (const ps of proxyStats.slice(0, 5)) {
        console.log(`    ${chalk.dim(ps.proxy)}: ${ps.count} requests`);
      }
    }
    
    console.log('');
    catalog.close();
  });

/**
 * CONFIG command
 */
program
  .command('config')
  .description('Manage configuration')
  .option('--show', 'Show current config')
  .option('--pia <credentials>', 'Set PIA credentials (username:password)')
  .option('--add-proxy <url>', 'Add a custom proxy')
  .option('--strategy <strategy>', 'Set rotation strategy (round-robin, random, least-used)')
  .option('--clear-proxies', 'Clear all proxies')
  .action(async (options) => {
    const configPath = path.join(process.cwd(), 'config', 'settings.json');
    
    // Load existing config
    let config = { proxy: { enabled: false, strategy: 'round-robin', pia: {}, custom: [] } };
    try {
      const data = await fs.readFile(configPath, 'utf8');
      config = JSON.parse(data);
    } catch {
      // No config yet
    }
    
    if (options.show) {
      console.log(chalk.cyan('\n⚙️ Current Configuration'));
      const display = { ...config };
      if (display.proxy?.pia?.password) {
        display.proxy.pia.password = '****';
      }
      console.log(JSON.stringify(display, null, 2));
      return;
    }
    
    let changed = false;
    
    if (options.pia) {
      const [username, password] = options.pia.split(':');
      config.proxy.enabled = true;
      config.proxy.pia = { username, password };
      console.log(chalk.green('✓ PIA credentials set'));
      changed = true;
    }
    
    if (options.addProxy) {
      config.proxy.enabled = true;
      config.proxy.custom = config.proxy.custom || [];
      config.proxy.custom.push(options.addProxy);
      console.log(chalk.green(`✓ Added proxy: ${options.addProxy}`));
      changed = true;
    }
    
    if (options.strategy) {
      config.proxy.strategy = options.strategy;
      console.log(chalk.green(`✓ Strategy set to: ${options.strategy}`));
      changed = true;
    }
    
    if (options.clearProxies) {
      config.proxy = { enabled: false, strategy: 'round-robin', pia: {}, custom: [] };
      console.log(chalk.green('✓ Proxies cleared'));
      changed = true;
    }
    
    if (changed) {
      await fs.mkdir(path.dirname(configPath), { recursive: true });
      await fs.writeFile(configPath, JSON.stringify(config, null, 2));
      console.log(chalk.dim(`Saved to ${configPath}`));
    } else {
      program.commands.find(c => c.name() === 'config').help();
    }
  });

// Run
program.parse();
