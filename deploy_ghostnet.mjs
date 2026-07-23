/**
 * Deploy IP Registry contract to Tezos Ghostnet
 * Uses a temporary test key — NOT your real wallet
 * Owner is set to your Temple wallet address
 */

import { TezosToolkit } from '@taquito/taquito';
import { InMemorySigner } from '@taquito/signer';
import { b58cencode, prefix } from '@taquito/utils';
import crypto from 'crypto';

const GHOSTNET_RPC = 'https://ghostnet.tezos.marigold.dev';
const OWNER_ADDRESS = 'tz1bmw3igCLN8N6CqgLBzJ9dyRb79E2Tdu5Q';

const CONTRACT_MICHELINE = [
  {"prim":"parameter","args":[{"prim":"or","args":[{"prim":"or","args":[{"prim":"pair","args":[{"prim":"string"},{"prim":"bytes"}],"annots":["%register"]},{"prim":"bytes","annots":["%set_master_hash"]}]},{"prim":"address","annots":["%transfer_ownership"]}]}]},
  {"prim":"storage","args":[{"prim":"pair","args":[{"prim":"address","annots":["%owner"]},{"prim":"pair","args":[{"prim":"big_map","args":[{"prim":"string"},{"prim":"bytes"}],"annots":["%registry"]},{"prim":"bytes","annots":["%master_hash"]}]}]}]},
  {"prim":"code","args":[[
    {"prim":"UNPAIR"},
    {"prim":"IF_LEFT","args":[
      [{"prim":"IF_LEFT","args":[
        [
          {"prim":"DUP","args":[{"int":"2"}]},{"prim":"CAR"},{"prim":"SENDER"},{"prim":"COMPARE"},{"prim":"EQ"},
          {"prim":"IF","args":[[],[{"prim":"PUSH","args":[{"prim":"string"},{"string":"NOT_OWNER"}]},{"prim":"FAILWITH"}]]},
          {"prim":"UNPAIR"},
          {"prim":"DIG","args":[{"int":"2"}]},{"prim":"UNPAIR"},{"prim":"SWAP"},{"prim":"UNPAIR"},
          {"prim":"DIG","args":[{"int":"3"}]},{"prim":"DIG","args":[{"int":"4"}]},{"prim":"SOME"},{"prim":"SWAP"},{"prim":"UPDATE"},
          {"prim":"PAIR"},{"prim":"SWAP"},{"prim":"PAIR"},
          {"prim":"NIL","args":[{"prim":"operation"}]},{"prim":"PAIR"}
        ],
        [
          {"prim":"DUP","args":[{"int":"2"}]},{"prim":"CAR"},{"prim":"SENDER"},{"prim":"COMPARE"},{"prim":"EQ"},
          {"prim":"IF","args":[[],[{"prim":"PUSH","args":[{"prim":"string"},{"string":"NOT_OWNER"}]},{"prim":"FAILWITH"}]]},
          {"prim":"SWAP"},{"prim":"UNPAIR"},{"prim":"SWAP"},{"prim":"CAR"},
          {"prim":"DIG","args":[{"int":"2"}]},{"prim":"SWAP"},{"prim":"PAIR"},{"prim":"SWAP"},{"prim":"PAIR"},
          {"prim":"NIL","args":[{"prim":"operation"}]},{"prim":"PAIR"}
        ]
      ]}],
      [
        {"prim":"DUP","args":[{"int":"2"}]},{"prim":"CAR"},{"prim":"SENDER"},{"prim":"COMPARE"},{"prim":"EQ"},
        {"prim":"IF","args":[[],[{"prim":"PUSH","args":[{"prim":"string"},{"string":"NOT_OWNER"}]},{"prim":"FAILWITH"}]]},
        {"prim":"SWAP"},{"prim":"CDR"},{"prim":"SWAP"},{"prim":"PAIR"},
        {"prim":"NIL","args":[{"prim":"operation"}]},{"prim":"PAIR"}
      ]
    ]}
  ]]}
];

const INIT_STORAGE = {
  "prim": "Pair",
  "args": [
    {"string": OWNER_ADDRESS},
    {"prim": "Pair", "args": [[], {"bytes": ""}]}
  ]
};

async function fundFromFaucet(address) {
  console.log('  Requesting test tez from Ghostnet faucet...');
  try {
    const res = await fetch('https://faucet.ghostnet.teztnets.com/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ address }),
    });
    if (res.ok) {
      const data = await res.json();
      console.log('  Faucet response: ' + JSON.stringify(data).slice(0, 200));
      return true;
    }
    console.log('  Faucet returned: ' + res.status);
    return false;
  } catch (e) {
    console.log('  Faucet request failed: ' + e.message);
    return false;
  }
}

async function waitForBalance(Tezos, address, maxAttempts = 30) {
  for (let i = 0; i < maxAttempts; i++) {
    try {
      const bal = await Tezos.tz.getBalance(address);
      const tez = bal.toNumber() / 1_000_000;
      if (tez >= 1) {
        console.log('  Balance confirmed: ' + tez.toFixed(2) + ' tez');
        return true;
      }
    } catch (e) {}
    if (i < maxAttempts - 1) {
      process.stdout.write('  Waiting for funds... (' + (i+1) + '/' + maxAttempts + ')\r');
      await new Promise(r => setTimeout(r, 5000));
    }
  }
  return false;
}

async function main() {
  console.log('='.repeat(60));
  console.log('TEZOS IP REGISTRY — Ghostnet Deploy');
  console.log('Contract owner: ' + OWNER_ADDRESS);
  console.log('='.repeat(60));

  // Generate a fresh ed25519 key for deployment
  console.log('\n[1] Generating temporary deployer key...');
  const seed = crypto.randomBytes(32);
  const secretKey = b58cencode(seed, prefix.edsk2);

  const signer = new InMemorySigner(secretKey);
  const Tezos = new TezosToolkit(GHOSTNET_RPC);
  Tezos.setProvider({ signer });

  const deployerAddress = await signer.publicKeyHash();
  console.log('  Deployer (temp): ' + deployerAddress);

  // Fund from faucet
  console.log('\n[2] Funding deployer from Ghostnet faucet...');
  const funded = await fundFromFaucet(deployerAddress);

  if (!funded) {
    console.log('\n  Auto-funding failed. Manual steps:');
    console.log('  1. Go to: https://faucet.ghostnet.teztnets.com/');
    console.log('  2. Paste: ' + deployerAddress);
    console.log('  3. Click "Request funds"');
    console.log('  4. Run this script again');
    process.exit(1);
  }

  // Wait for balance
  console.log('\n[3] Waiting for balance confirmation...');
  const hasBalance = await waitForBalance(Tezos, deployerAddress);

  if (!hasBalance) {
    console.log('\n  Balance not confirmed yet. Try again in 30 seconds.');
    process.exit(1);
  }

  // Deploy
  console.log('\n[4] Deploying contract...');
  console.log('  Estimating gas...');

  try {
    const op = await Tezos.contract.originate({
      code: CONTRACT_MICHELINE,
      init: INIT_STORAGE,
    });

    console.log('  TX hash: ' + op.hash);
    console.log('  Waiting for confirmation (~30s)...');

    const contract = await op.contract();
    const ktAddress = contract.address;

    console.log('\n' + '='.repeat(60));
    console.log('  CONTRACT DEPLOYED ON GHOSTNET!');
    console.log('');
    console.log('  Contract:  ' + ktAddress);
    console.log('  TX:        ' + op.hash);
    console.log('  Owner:     ' + OWNER_ADDRESS);
    console.log('');
    console.log('  Explorer:  https://ghostnet.tzkt.io/' + ktAddress);
    console.log('  Operation: https://ghostnet.tzkt.io/' + op.hash);
    console.log('='.repeat(60));

    console.log('\n  NEXT STEPS:');
    console.log('  1. Open register_ip.html in Chrome (with Temple)');
    console.log('  2. Select GHOSTNET');
    console.log('  3. Connect Temple wallet');
    console.log('  4. Paste contract address: ' + ktAddress);
    console.log('  5. Click "Master Hash (1 tx)" to register all IP');

  } catch (err) {
    console.error('\n  Deploy failed: ' + err.message);
    if (err.errors) {
      for (const e of err.errors) {
        console.error('    ' + JSON.stringify(e));
      }
    }
    process.exit(1);
  }
}

main().catch(err => {
  console.error('Fatal: ' + err.message);
  process.exit(1);
});
