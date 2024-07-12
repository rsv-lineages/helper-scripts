import yaml, glob

if __name__=="__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--input-dir', required=True)
    parser.add_argument('--aux-input-dir')
    parser.add_argument('--use-short-name', action='store_true', default=False)
    parser.add_argument('--flat-output', action='store_true', default=False)
    parser.add_argument('--output-tsv')
    args = parser.parse_args()

    yml_files = glob.glob(args.input_dir+'/*yml')
    clades = {}
    for yfile in yml_files:
        with open(yfile, 'r') as stream:
            yaml_data = yaml.safe_load(stream)
            clades[yaml_data['name']] = {'parent': yaml_data['parent'],
                                        'defining_muts':{(x['locus'], x['position']):x['state']
                                        for x in yaml_data.get('defining_mutations', [])}}
            for k in ['alias_of', 'short_name']:
                if k in yaml_data:
                    clades[yaml_data['name']][k] = yaml_data[k]

    if args.aux_input_dir:
        yml_files = glob.glob(args.aux_input_dir+'/*yml')
        subclades = {}
        for yfile in yml_files:
            with open(yfile, 'r') as stream:
                yaml_data = yaml.safe_load(stream)
                subclades[yaml_data['name']] = {'parent': yaml_data['parent'],
                                            'defining_muts':{(x['locus'], x['position']):x['state']
                                            for x in yaml_data['defining_mutations']}}

    tsv_file = open(args.output_tsv, 'w')
    sep = '\t'
    tsv_file.write(sep.join(['clade','gene','site','alt'])+'\n')

    if args.flat_output:
        if args.aux_input_dir:
            all_aux_muts = {}
            for c in sorted(subclades.keys()):
                if subclades[c].get('parent', 'none')=='none':
                    all_aux_muts[c] = subclades[c]['defining_muts']
                else:
                    all_aux_muts[c] = {k:v for k,v in all_aux_muts[subclades[c]['parent']].items()}
                for (locus, position), state in subclades[c]['defining_muts'].items():
                    all_aux_muts[c][(locus, position)] = state

        all_muts = {}
        for c in sorted(clades.keys()):
            if 'alias_of' in clades[c] and clades[c]['alias_of'] in subclades:
                all_muts[c] = {k:v for k,v in all_aux_muts[clades[c]['alias_of']].items()}
            else:
                if clades[c].get('parent', 'none')=='none':
                    all_muts[c] = clades[c]['defining_muts']
                else:
                    all_muts[c] = {k:v for k,v in all_muts.get(clades[c]['parent'],{}).items()}
                for (locus, position), state in clades[c]['defining_muts'].items():
                    all_muts[c][(locus, position)] = state

            out_name = c if not args.use_short_name else clades[c].get('short_name', c)
            for (locus, position), state in sorted(all_muts[c].items()):
                tsv_file.write(sep.join([out_name, locus, str(position),state])+'\n')

    else:
        for c in sorted(clades.keys()):
            if clades[c].get('parent', 'none')!='none':
                tsv_file.write(sep.join([c,'clade', clades[c]['parent'],''])+'\n')
            for (locus, position), state in clades[c]['defining_muts'].items():
                tsv_file.write(sep.join([c, locus, str(position),state])+'\n')

    tsv_file.close()