from typing import Dict, List, Tuple, Union
from flask import Flask, request, url_for

from common.decorators import templated

import os
import json
import toml

import requests
import py3Dmol


def create_app():
    """
    Creates an instance of the Flask app, and associated configuration and blueprints registration for specific routes. 

    Configuration includes

    - Relevant secrets stored in the config.toml file
    - Storing in configuration a set of credentials for AWS (decided upon by the environment of the application e.g. development, live)
    
    Returns:
            A configured instance of the Flask app

    """
    app = Flask(__name__)

    app.config.from_file('config.toml', toml.load)
    # removing whitespace from templated returns    
    app.jinja_env.trim_blocks = True
    app.jinja_env.lstrip_blocks = True

    #print (f"Data held in memory for app.data is {round(dataset_size / 1024, 1)}MB")
    
    app.data = {
        'receptors': [],
        'loci': []
    }

    return app

app = create_app()


@app.route('/comparisons/')
@app.route('/comparisons')
#@templated('comparisons_home')
def comparisons_home(api=False):
    """
    This is the handler for the comparisons homepage. 
    """
    data = app.data.copy()

    return {
        'message': 'Coming soon!'
    }



@app.route('/comparisons/tcr/')
@app.route('/comparisons/tcr')
#@templated('tcr_comparison_home')
def tcr_comparisons_home(api=False):
    """
    This is the handler for the comparisons TCR homepage. 
    """
    data = app.data.copy()

    return {
        'message': 'Coming soon!'
    }


def fetch_coordinates(pdb_code:str, domain:str, apo_holo:str):
    """
    This function fetches the coordinates for the TCRs from the coordinate server. 
    """
    data = None
    if apo_holo == 'apo':
        apo_holo = 'apo_pmhc'
    elif apo_holo == 'holo':
        apo_holo = 'holo_pmhc_tcr'

    url_base = "https://raw.githubusercontent.com/drchristhorpe/apo_vs_holo_pmhc_tcr/main/structures"
    apo_peptide_url = f"{url_base}/{apo_holo}/clean/{pdb_code}_1_{domain}.pdb"

    r = requests.get(apo_peptide_url)
    if r.status_code == 200:
        data = r.text

    return data


def peptide_comparison(apo_pdb_code:str, holo_pdb_code:str):
    """
    This function outputs the HTML for the peptide comparison interactive viewer. 
    """
    html = None

    apo_peptide = fetch_coordinates(apo_pdb_code, 'peptide', 'apo')
    holo_peptide = fetch_coordinates(holo_pdb_code, 'peptide', 'holo')

    if apo_peptide and holo_peptide:
        view = py3Dmol.view(width=800, height=500)
        view.addModelsAsFrames(apo_peptide)
        view.addModelsAsFrames(holo_peptide)
        view.setStyle({'model': 0}, {"stick": {'colorscheme': 'greenCarbon'}})
        view.setStyle({'model': 1}, {"stick": {'colorscheme': 'yellowCarbon'}})
        view.zoomTo()
        html = view.write_html()
        
    return html

@app.route('/comparisons/tcr/<string:apo_pdb_code>_vs_<string:holo_pdb_code>/')
@app.route('/comparisons/tcr/<string:apo_pdb_code>_vs_<string:holo_pdb_code>')
@templated('tcr_comparison_page')
def tcr_comparison_page(apo_pdb_code, holo_pdb_code, api=False):
    """
    This is the handler for the TCR comparison page. 
    """
    data = app.data.copy()

    # do some redirections
    
    # if apo and holo are switched, redirect to the correct page
    # if the apo and holo are the same, redirect to a page saying they're the same
    # if the apo and holo are not in the list, redirect to a page saying they're not in the list
    # if one or the other are in the list, redirect to the page with a suggestion for the other


    return {
        'apo_pdb_code':apo_pdb_code,
        'holo_pdb_code':holo_pdb_code,
        'apo_holo_peptide_comparison':peptide_comparison(apo_pdb_code, holo_pdb_code),
    }