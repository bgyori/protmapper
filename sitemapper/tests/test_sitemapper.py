from __future__ import absolute_import, print_function, unicode_literals
from builtins import dict, str
from nose.tools import raises
from sitemapper.api import SiteMapper, _validate_sites, Site, MappedSite

@raises(ValueError)
def test_invalid_residue():
    sm = SiteMapper()
    sm.map_to_human_ref('MAPK1', 'HGNC', 'B', '185')

@raises(ValueError)
def test_invalid_position():
    sm = SiteMapper()
    sm.map_to_human_ref('MAPK1', 'HGNC', 'T', 'foo')

@raises(ValueError)
def test_invalid_prot_ns():
    sm = SiteMapper()
    sm.map_to_human_ref('MAPK1', 'hgncsymb', 'T', '185')

def test_validate_sites():
    sites = _validate_sites([('T', '185'), ('Y', '187')])
    assert len(sites) == 2
    assert isinstance(sites[0], Site)
    assert sites[0].residue == 'T'
    assert sites[0].position == '185'
    assert isinstance(sites[1], Site)
    assert sites[1].residue == 'Y'
    assert sites[1].position == '187'


def test_check_agent_mod_up_id():
    sm = SiteMapper()
    ms = sm.map_to_human_ref('P28482', 'uniprot', 'T', '185')
    assert instance(ms, MappedSite)
    assert ms.up_id == 'P28482'
    assert ms.hgnc_name is None
    assert ms.valid is True
    assert ms.orig_res == 'T'
    assert ms.orig_pos == '185'
    assert ms.mapped_res == 'T'
    assert ms.mapped_pos == '185'
    assert ms.description == 'VALID'

    ms = sm.map_to_human_ref('P28482', 'uniprot', 'T', '183')
    assert instance(ms, MappedSite)
    assert ms.up_id == 'P28482'
    assert ms.hgnc_name is None
    assert ms.valid is False
    assert ms.orig_res == 'T'
    assert ms.orig_pos == '183'
    assert ms.mapped_res == 'T'
    assert ms.mapped_pos == '185'
    assert ms.description == 'INFERRED_MOUSE_SITE'


def test_check_agent_mod_hgnc():
    sm = SiteMapper()
    ms = sm.map_to_human_ref('MAPK1', 'hgnc', 'T', '185')
    assert instance(ms, MappedSite)
    assert ms.up_id == 'P28482'
    assert ms.hgnc_name == 'MAPK1'
    assert ms.valid is True
    assert ms.orig_res == 'T'
    assert ms.orig_pos == '185'
    assert ms.mapped_res == 'T'
    assert ms.mapped_pos == '185'
    assert ms.description == 'VALID'

    ms = sm.map_to_human_ref('MAPK1', 'hgnc', 'T', '183')
    assert instance(ms, MappedSite)
    assert ms.up_id == 'P28482'
    assert ms.hgnc_name == 'MAPK1'
    assert ms.valid is False
    assert ms.orig_res == 'T'
    assert ms.orig_pos == '183'
    assert ms.mapped_res == 'T'
    assert ms.mapped_pos == '185'
    assert ms.description == 'INFERRED_MOUSE_SITE'

    """
    res_valid = sm._map_agent_sites(mapk1_valid)
    assert len(res_valid) == 2
    assert res_valid[0] == []
    assert res_valid[1].matches(mapk1_valid)
    """

    """
    res_invalid = sm._map_agent_sites(mapk1_invalid)
    assert len(res_invalid) == 2
    assert isinstance(res_invalid[0], list)
    assert isinstance(res_invalid[1], Agent)
    invalid_sites = res_invalid[0]
    assert len(invalid_sites) == 2
    map183 = invalid_sites[0]
    assert map183[0] == ('MAPK1', 'T', '183')
    assert len(map183[1]) == 3
    assert map183[1][0] == 'T'
    assert map183[1][1] == '185'
    map185 = invalid_sites[1]
    assert map185[0] == ('MAPK1', 'Y', '185')
    assert len(map185[1]) == 3
    assert map185[1][0] == 'Y'
    assert map185[1][1] == '187'
    new_agent = res_invalid[1]
    """

"""
def test_site_map_modification():
    mapk1_invalid = Agent('MAPK1',
                          mods=[ModCondition('phosphorylation', 'T', '183'),
                                ModCondition('phosphorylation', 'Y', '185')],
                          db_refs={'UP': 'P28482'})
    mapk3_invalid = Agent('MAPK3',
                          mods=[ModCondition('phosphorylation', 'T', '201')],
                          db_refs={'UP': 'P27361'})
    map2k1_invalid = Agent('MAP2K1',
                           mods=[ModCondition('phosphorylation', 'S', '217'),
                                 ModCondition('phosphorylation', 'S', '221')],
                           db_refs={'UP': 'Q02750'})

    st1 = Phosphorylation(mapk1_invalid, mapk3_invalid, 'Y', '203')
    st2 = Phosphorylation(map2k1_invalid, mapk1_invalid, 'Y', '218')
    res = sm.map_sites([st1, st2])

    assert len(res) == 2
    valid_stmts = res[0]
    mapped_stmts = res[1]
    assert isinstance(valid_stmts, list)
    assert isinstance(mapped_stmts, list)
    assert len(valid_stmts) == 0
    assert len(mapped_stmts) == 2
    # MAPK1 -> MAPK3
    mapped_stmt1 = mapped_stmts[0]
    assert isinstance(mapped_stmt1, MappedStatement)
    assert mapped_stmt1.original_stmt == st1
    assert isinstance(mapped_stmt1.mapped_mods, list)
    assert len(mapped_stmt1.mapped_mods) == 4, \
        "Got %d mapped mods." % mapped_stmt1.mapped_mods  # FIXME
    ms = mapped_stmt1.mapped_stmt
    assert isinstance(ms, Statement)
    agent1 = ms.enz
    agent2 = ms.sub
    assert agent1.name == 'MAPK1'
    assert len(agent1.mods) == 2
    assert agent1.mods[0].matches(ModCondition('phosphorylation', 'T', '185'))
    assert agent1.mods[1].matches(ModCondition('phosphorylation', 'Y', '187'))
    assert agent2.mods[0].matches(ModCondition('phosphorylation', 'T', '202'))
    assert ms.residue == 'Y'
    assert ms.position == '204'

    # MAP2K1 -> MAPK1
    mapped_stmt2 = mapped_stmts[1]
    assert isinstance(mapped_stmt2, MappedStatement)
    assert mapped_stmt2.original_stmt == st2
    assert isinstance(mapped_stmt2.mapped_mods, list)
    assert len(mapped_stmt2.mapped_mods) == 5, \
        "Got %d mapped mods." % mapped_stmt1.mapped_mods  # FIXME
    ms = mapped_stmt2.mapped_stmt
    assert isinstance(ms, Statement)
    agent1 = ms.enz
    agent2 = ms.sub
    assert agent1.name == 'MAP2K1'
    assert len(agent1.mods) == 2
    assert agent1.mods[0].matches(ModCondition('phosphorylation', 'S', '218'))
    assert agent1.mods[1].matches(ModCondition('phosphorylation', 'S', '222'))
    assert len(agent2.mods) == 2
    assert agent2.mods[0].matches(ModCondition('phosphorylation', 'T', '185'))
    assert agent2.mods[1].matches(ModCondition('phosphorylation', 'Y', '187'))
    # The incorrect phosphorylation residue is passed through to the new
    # statement unchanged
    assert ms.residue == 'Y'
    assert ms.position == '218'
    # Check for unicode
    assert unicode_strs((mapk1_invalid, mapk3_invalid, map2k1_invalid, st1,
                         st2, res, valid_stmts, mapped_stmts))

def test_site_map_activity_modification():
    mc = [ModCondition('phosphorylation', 'T', '183'),
          ModCondition('phosphorylation', 'Y', '185')]
    mapk1 = Agent('MAPK1', mods=mc, db_refs={'UP': 'P28482'})

    st1 = ActiveForm(mapk1, 'kinase', True)
    (valid, mapped) = sm.map_sites([st1])
    assert len(valid) == 0
    assert len(mapped) == 1
    ms = mapped[0]
    assert ms.mapped_mods[0][0] == ('MAPK1', 'T', '183')
    assert ms.mapped_mods[0][1][0] == 'T'
    assert ms.mapped_mods[0][1][1] == '185'
    assert ms.mapped_mods[1][0] == ('MAPK1', 'Y', '185')
    assert ms.mapped_mods[1][1][0] == 'Y'
    assert ms.mapped_mods[1][1][1] == '187'
    assert ms.original_stmt == st1
    assert ms.mapped_stmt.agent.mods[0].matches(ModCondition('phosphorylation',
                                                             'T', '185'))
    assert ms.mapped_stmt.agent.mods[1].matches(ModCondition('phosphorylation',
                                                             'Y', '187'))
    assert unicode_strs((mc, mapk1, st1, valid, mapped))

def test_site_map_selfmodification():
    mapk1_invalid = Agent('MAPK1',
                          mods=[ModCondition('phosphorylation', 'T', '183')],
                          db_refs={'UP': 'P28482'})
    st1 = SelfModification(mapk1_invalid, 'Y', '185')
    (valid, mapped) = sm.map_sites([st1])
    assert len(valid) == 0
    assert len(mapped) == 1
    mapped_stmt = mapped[0]
    assert mapped_stmt.mapped_mods[0][0] == ('MAPK1', 'T', '183')
    assert mapped_stmt.mapped_mods[0][1][0] == 'T'
    assert mapped_stmt.mapped_mods[0][1][1] == '185'
    assert mapped_stmt.mapped_mods[1][0] == ('MAPK1', 'Y', '185')
    assert mapped_stmt.mapped_mods[1][1][0] == 'Y'
    assert mapped_stmt.mapped_mods[1][1][1] == '187'
    assert mapped_stmt.original_stmt == st1
    ms = mapped_stmt.mapped_stmt
    agent1 = ms.enz
    assert agent1.mods[0].matches(ModCondition('phosphorylation', 'T', '185'))
    assert ms.residue == 'Y'
    assert ms.position == '187'
    assert unicode_strs((mapk1_invalid, st1, valid, mapped))

# The following Statements are all handled by the same block of code and hence
# can be tested in similar fashion

def test_site_map_complex():
    (mapk1_invalid, mapk3_invalid) = get_invalid_mapks()
    st1 = Complex([mapk1_invalid, mapk3_invalid])
    res = sm.map_sites([st1])
    check_validated_mapks(res, st1)

def test_site_map_gef():
    (mapk1_invalid, mapk3_invalid) = get_invalid_mapks()
    st1 = Gef(mapk1_invalid, mapk3_invalid)
    res = sm.map_sites([st1])
    check_validated_mapks(res, st1)

def test_site_map_gap():
    (mapk1_invalid, mapk3_invalid) = get_invalid_mapks()
    st1 = Gap(mapk1_invalid, mapk3_invalid)
    res = sm.map_sites([st1])
    check_validated_mapks(res, st1)

def test_site_map_activation():
    (mapk1_invalid, mapk3_invalid) = get_invalid_mapks()
    st1 = Activation(mapk1_invalid, mapk3_invalid, 'kinase')
    res = sm.map_sites([st1])
    check_validated_mapks(res, st1)

def test_site_map_hgnc():
    (mapk1_invalid, mapk3_invalid) = get_invalid_mapks()
    mapk1_invalid.db_refs = {'HGNC': '6871'}
    st1 = ActiveForm(mapk1_invalid, 'kinase', True)
    (valid, mapped) = sm.map_sites([st1])
    assert len(valid) == 0
    assert len(mapped) == 1


def test_site_map_within_bound_condition():
    # Here, we test to make sure that agents within a bound condition are
    # site-mapped
    (mapk1_invalid, mapk3_invalid) = get_invalid_mapks()

    # Add an agent to the bound condition for the object of the statement
    mapk3_invalid.bound_conditions = [BoundCondition(mapk1_invalid)]
    st1 = Activation(mapk1_invalid, mapk3_invalid, 'kinase')

    # Map sites
    res = sm.map_sites([st1])

    # Extract the mapped statement
    mapped_statements = res[1]
    assert len(mapped_statements) == 1
    mapped_s = mapped_statements[0].mapped_stmt

    # Verify that the agent in the object's bound condition got site-mapped
    validate_mapk1(mapped_s.obj.bound_conditions[0].agent)


def get_invalid_mapks():
    mapk1_invalid = Agent('MAPK1',
                          mods=[ModCondition('phosphorylation', 'T', '183'),
                                ModCondition('phosphorylation', 'Y', '185')],
                          db_refs={'UP': 'P28482'})
    mapk3_invalid = Agent('MAPK3',
                          mods=[ModCondition('phosphorylation', 'T', '201'),
                                ModCondition('phosphorylation', 'Y', '203')],
                          db_refs={'UP': 'P27361'})
    assert unicode_strs((mapk1_invalid, mapk3_invalid))
    return (mapk1_invalid, mapk3_invalid)

def check_validated_mapks(res, st1):
    assert len(res) == 2
    valid_stmts = res[0]
    mapped_stmts = res[1]
    assert isinstance(valid_stmts, list)
    assert isinstance(mapped_stmts, list)
    assert len(valid_stmts) == 0
    assert len(mapped_stmts) == 1
    mapped_stmt = mapped_stmts[0]
    assert isinstance(mapped_stmt, MappedStatement)
    assert mapped_stmt.original_stmt == st1
    assert isinstance(mapped_stmt.mapped_mods, list)
    assert len(mapped_stmt.mapped_mods) == 4
    ms = mapped_stmt.mapped_stmt
    assert isinstance(ms, Statement)
    agents = ms.agent_list()
    assert len(agents) == 2
    agent1 = agents[0]
    agent2 = agents[1]
    validate_mapk1(agent1)
    assert agent2.mods[0].matches(ModCondition('phosphorylation', 'T', '202'))
    assert agent2.mods[1].matches(ModCondition('phosphorylation', 'Y', '204'))
    assert unicode_strs((res, st1))


def validate_mapk1(agent1):
    assert agent1.name == 'MAPK1'
    assert len(agent1.mods) == 2
    assert agent1.mods[0].matches(ModCondition('phosphorylation', 'T', '185'))
    assert agent1.mods[1].matches(ModCondition('phosphorylation', 'Y', '187'))
"""
