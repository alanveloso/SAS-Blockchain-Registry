'use strict';

const { WorkloadModuleBase } = require('@hyperledger/caliper-core');

class CBSDRegistryWorkload extends WorkloadModuleBase {
    constructor() {
        super();
        this.cbsdId = 1;
    }

    async initializeWorkloadModule(workerIndex, totalWorkers, roundIndex, roundArguments, sutAdapter, sutContext) {
        this.action = roundArguments.action;
        this.cbsdId = workerIndex * 1000 + roundIndex * 100 + 1;
        this.cbsdAddress = '0x0000000000000000000000000000000000000001';
    }

    async submitTransaction() {
        if (this.action === 'register') {
            return this.sutAdapter.sendRequests([
                {
                    contract: 'CBSDRegistry',
                    verb: 'registerCBSD',
                    args: [this.cbsdId.toString(), this.cbsdAddress, '1000'],
                }
            ]);
        } else if (this.action === 'updateGrant') {
            return this.sutAdapter.sendRequests([
                {
                    contract: 'CBSDRegistry',
                    verb: 'updateGrantAmount',
                    args: [this.cbsdId.toString(), '2000'],
                }
            ]);
        } else if (this.action === 'updateStatus') {
            return this.sutAdapter.sendRequests([
                {
                    contract: 'CBSDRegistry',
                    verb: 'updateStatus',
                    args: [this.cbsdId.toString(), 'active'],
                }
            ]);
        }
    }
}

function createWorkloadModule() {
    return new CBSDRegistryWorkload();
}

module.exports.createWorkloadModule = createWorkloadModule; 