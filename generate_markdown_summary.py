#! python
#%%
import yaml
import glob


def generate_url(accession):
    if accession.startswith("PP_"):
        return f"https://pathoplexus.org/seq/{accession}"
    else:
        return f"https://www.ncbi.nlm.nih.gov/nuccore/{accession}"


def generate_lineage_md(clade, lineage):
    lines = []
    lines.append(f"## {clade['name']}")
    lines.append(f" * parent: [{clade['parent']}](#{clade['parent'].replace('.', '')})")
    snp_str = ', '.join(f"{x['locus']}:{x['position']}{x['state']}" for x in clade['defining_mutations'])
    lines.append(f" * defining mutations or substitutions: {snp_str}")
    if "clade" in clade and clade['clade'] != "none":
        lines.append(f" * clade: {clade['clade']}")

    ref_seqs = [f"[{x}]({generate_url(x)})" for x in clade['representatives']]
    if len(ref_seqs)==1:
        lines.append(f" * representative sequence: {ref_seqs[0]}")
    elif len(ref_seqs)>1:
        lines.append(f" * representative sequences:")
        for r in ref_seqs:
            lines.append(f"   - {r}")
    lines.append(f" * [View in Nextstrain](https://nextstrain.org/rsv/{lineage.lower()}/genome?branchLabel=clade&c=clade&label=clade:{clade['name']})")
    return '\n'.join(lines) + '\n'

if __name__=="__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--input-dir', required=True)
    parser.add_argument('--lineage')
    args = parser.parse_args()

    clades = []
    # Iterate through all lineage definition files
    for yaml_file in sorted(glob.glob(f"{args.input_dir}/*.yml")):
        with open(yaml_file, 'r') as stream:
            yaml_data = yaml.safe_load(stream)
        clades.append(yaml_data)

    clades.sort(key=lambda x:x['name'])
    clade_lineage_map = [(x['clade'], x['name'], x['unaliased_name'])
                         for x in clades if 'clade' in x and x['clade'] != 'none']
    # Write to json file
    with open('.auto-generated/clades.md', 'w') as outfile:
        outfile.write("# Summary of designated clades\n")

        for clade in clades:
            outfile.write(generate_lineage_md(clade, args.lineage) + '\n')

    # representative strains
    with open('representatives.txt', 'w') as outfile:
        for clade in clades:
            outfile.write("\n".join(clade["representatives"]) + ("\n" if len(clade["representatives"]) else ""))

## usage:
## python ../helper-scripts/generate_markdown_summary.py --lineage b --input-dir lineages
