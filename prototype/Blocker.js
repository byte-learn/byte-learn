const fs = require('fs');
const AdBlockClient = require('adblock-rs');


class Blocker {
    constructor({adRules=[], trackingRules=[]}) {
        this._adrules = [];
        this._trrules = [];
        for (const rule of adRules){
            const r = fs.readFileSync(rule, { encoding: 'utf-8' }).split('\n');
            this._adrules = this._adrules.concat(r);
        }
        for (const rule of trackingRules){
            const r = fs.readFileSync(rule, { encoding: 'utf-8' }).split('\n');
            this._trrules = this._trrules.concat(r);
        }
        const filterSetAd = new AdBlockClient.FilterSet(true);
        const filterSetTracker = new AdBlockClient.FilterSet(true);
        filterSetAd.addFilters(this._adrules);
        filterSetTracker.addFilters(this._trrules);
        this._adclient = new AdBlockClient.Engine(filterSetAd, true);
        this._trclient = new AdBlockClient.Engine(filterSetTracker, true);
    }

    check({script_url, main_url, resource_type}) {
        for (const client of [this._adclient, this._trclient]){
            const {matched} = client.check(script_url, main_url, resource_type, true);
            if (matched) {
                if (client === this._adclient)
                    return {matched, category: 'ad'}
                else
                    return {matched, category: 'tracker'}
            }  
        }
        return {matched: false, category: null} 
    }
}


module.exports = {Blocker}