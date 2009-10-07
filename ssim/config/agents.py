import ldap

def save(l, config, agent_list):
    mod_attrs = []
    #add new elements
    for agent in agent_list:
        if agent not in config.elements:
            mod_attrs += [( ldap.MOD_ADD, 'symcElementConfigurationElementRef', agent.encode("utf-8") )]
            config.add_element(agent)
    #remove deleted elements
    for agent in config.elements:
        if agent not in agent_list:
            mod_attrs += [( ldap.MOD_DELETE, 'symcElementConfigurationElementRef', agent )]
            config.remove_element(agent)
    #save data
    if len(mod_attrs) > 0:
        l.modify_s(config.dn, mod_attrs)