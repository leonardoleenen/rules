from rauth import OAuth1Service, OAuth2Service
from flask import current_app, url_for, request, redirect, session
import json

SERVICES_ROLES_MATRIX = [
    {
        "path": "/rulz/status/check/*",
        "user_profiles": [
            "Aplicacion",
            "ADMINISTRADOR",
            "EDITOR",
            "PUBLICADOR",
            "Usuario"
        ],
        "user_roles": [
            "PUBLICADOR",
            "ADMINISTRADOR",
            "EDITOR",
            "WriteEntity"
        ]
    },
    {
        "path": "/security/token/create",
        "user_profiles": [
            "ADMINISTRADOR",
            "EDITOR",
            "PUBLICADOR",
            "Usuario"
        ],
        "user_roles": [
            "PUBLICADOR",
            "ADMINISTRADOR",
            "EDITOR"
        ]
    },
    {
        "path": "/security/rxf/matrix",
        "user_profiles": [
            "ADMINISTRADOR",
            "EDITOR",
            "PUBLICADOR",
            "Usuario"
        ],
        "user_roles": [
            "PUBLICADOR",
            "ADMINISTRADOR",
            "EDITOR"
        ]
    },
    {
        "path": "/security/user/get_roles",
        "user_profiles": [
            "ADMINISTRADOR",
            "EDITOR",
            "PUBLICADOR",
            "Usuario"
        ],
        "user_roles": [
            "PUBLICADOR",
            "ADMINISTRADOR",
            "EDITOR"
        ]
    },
    {
        "path": "/anses/get_employee_office",
        "user_profiles": [
            "ADMINISTRADOR",
            "EDITOR",
            "PUBLICADOR",
            "Usuario"
        ],
        "user_roles": [
            "PUBLICADOR",
            "ADMINISTRADOR",
            "EDITOR"
        ]
    },
    {
        "path": "/anses/get_office_children",
        "user_profiles": [
            "ADMINISTRADOR",
            "EDITOR",
            "PUBLICADOR",
            "Usuario"
        ],
        "user_roles": [
            "PUBLICADOR",
            "ADMINISTRADOR",
            "EDITOR"
        ]
    },
    {
        "path": "/config/as_dict",
        "user_profiles": [
            "ADMINISTRADOR",
            "EDITOR",
            "PUBLICADOR",
            "Usuario"
        ],
        "user_roles": [
            "PUBLICADOR",
            "ADMINISTRADOR",
            "EDITOR"
        ]
    },
    {
        "path": "/config/*",
        "user_profiles": [
            "Aplicacion",
            "ADMINISTRADOR",
            "EDITOR",
            "PUBLICADOR",
            "Usuario"
        ],
        "user_roles": [
            "PUBLICADOR",
            "ADMINISTRADOR",
            "EDITOR"
        ]
    },
    {
        "path": "/rulz/rule",
        "user_profiles": [
            "Aplicacion",
            "ADMINISTRADOR",
            "EDITOR",
            "PUBLICADOR",
            "Usuario"
        ],
        "user_roles": [
            "PUBLICADOR",
            "ADMINISTRADOR",
            "EDITOR",
            "WriteRule"
        ]
    },
    {
        "path": "/rulz/entity",
        "user_profiles": [
            "Aplicacion",
            "ADMINISTRADOR",
            "EDITOR",
            "PUBLICADOR",
            "Usuario"
        ],
        "user_roles": [
            "PUBLICADOR",
            "ADMINISTRADOR",
            "EDITOR",
            "WriteEntity"
        ]
    },
    {
        "path": "/rulz/check/entity/attribute",
        "user_profiles": [
            "Aplicacion",
            "ADMINISTRADOR",
            "EDITOR",
            "PUBLICADOR",
            "Usuario"
        ],
        "user_roles": [
            "PUBLICADOR",
            "ADMINISTRADOR",
            "EDITOR",
            "WriteEntity"
        ]
    },
    {
        "path": "/rulz/change/entity/attribute",
        "user_profiles": [
            "Aplicacion",
            "ADMINISTRADOR",
            "EDITOR",
            "PUBLICADOR",
            "Usuario"
        ],
        "user_roles": [
            "PUBLICADOR",
            "ADMINISTRADOR",
            "EDITOR",
            "WriteEntity"
        ]
    },
    {
        "path": "/rulz/catalog",
        "user_profiles": [
            "Aplicacion",
            "ADMINISTRADOR",
            "EDITOR",
            "PUBLICADOR",
            "Usuario"
        ],
        "user_roles": [
            "PUBLICADOR",
            "ADMINISTRADOR",
            "EDITOR",
            "WriteCatalog"
        ]
    },
    {
        "path": "/rulz/table",
        "user_profiles": [
            "Aplicacion",
            "ADMINISTRADOR",
            "EDITOR",
            "PUBLICADOR",
            "Usuario"
        ],
        "user_roles": [
            "PUBLICADOR",
            "ADMINISTRADOR",
            "EDITOR",
            "WriteTable"
        ]
    },
    {
        "path": "/rulz/simulation",
        "user_profiles": [
            "Aplicacion",
            "ADMINISTRADOR",
            "EDITOR",
            "PUBLICADOR",
            "Usuario"
        ],
        "user_roles": [
            "PUBLICADOR",
            "ADMINISTRADOR",
            "EDITOR",
            "WriteSimulation"
        ]
    },
    {
        "path": "/rulz/simulation/model/get",
        "user_profiles": [
            "Aplicacion",
            "ADMINISTRADOR",
            "EDITOR",
            "PUBLICADOR",
            "Usuario"
        ],
        "user_roles": [
            "PUBLICADOR",
            "ADMINISTRADOR",
            "EDITOR",
            "WriteSimulation"
        ]
    },
    {
        "path": "/rulz/simulation/jsons",
        "user_profiles": [
            "Aplicacion",
            "ADMINISTRADOR",
            "EDITOR",
            "PUBLICADOR",
            "Usuario"
        ],
        "user_roles": [
            "PUBLICADOR",
            "ADMINISTRADOR",
            "EDITOR",
            "WriteSimulation"
        ]
    },
    {
        "path": "/rulz/list",
        "user_profiles": [
            "Aplicacion",
            "ADMINISTRADOR",
            "EDITOR",
            "PUBLICADOR",
            "Usuario"
        ],
        "user_roles": [
            "PUBLICADOR",
            "ADMINISTRADOR",
            "EDITOR",
            "WriteList"
        ]
    },
    {
        "path": "/rulz/function",
        "user_profiles": [
            "Aplicacion",
            "ADMINISTRADOR",
            "EDITOR",
            "PUBLICADOR",
            "Usuario"
        ],
        "user_roles": [
            "PUBLICADOR",
            "ADMINISTRADOR",
            "EDITOR",
            "WriteFunction"
        ]
    },
    {
        "path": "/rulz/function/test",
        "user_profiles": [
            "Aplicacion",
            "ADMINISTRADOR",
            "EDITOR",
            "PUBLICADOR",
            "Usuario"
        ],
        "user_roles": [
            "PUBLICADOR",
            "ADMINISTRADOR",
            "EDITOR",
            "WriteFunction"
        ]
    },
    {
        "path": "/rulz/formula",
        "user_profiles": [
            "Aplicacion",
            "ADMINISTRADOR",
            "EDITOR",
            "PUBLICADOR",
            "Usuario"
        ],
        "user_roles": [
            "PUBLICADOR",
            "ADMINISTRADOR",
            "EDITOR",
            "WriteFormula"
        ]
    },
    {
        "path": "/rulz/instrument",
        "user_profiles": [
            "Aplicacion",
            "ADMINISTRADOR",
            "EDITOR",
            "PUBLICADOR",
            "Usuario"
        ],
        "user_roles": [
            "PUBLICADOR",
            "ADMINISTRADOR",
            "EDITOR",
            "WriteInstrument"
        ]
    },
    {
        "path": "/rulz/instrument/file/delete",
        "user_profiles": [
            "Aplicacion",
            "ADMINISTRADOR",
            "EDITOR",
            "PUBLICADOR",
            "Usuario"
        ],
        "user_roles": [
            "PUBLICADOR",
            "ADMINISTRADOR",
            "EDITOR",
            "WriteInstrument"
        ]
    },
    {
        "path": "/rulz/simulate/*",
        "user_profiles": [
            "Aplicacion",
            "ADMINISTRADOR",
            "EDITOR",
            "PUBLICADOR",
            "Usuario"
        ],
        "user_roles": [
            "PUBLICADOR",
            "ADMINISTRADOR",
            "EDITOR",
            "RuleSimulate"
        ]
    },
    {
        "path": "/rulz/install/publication/*",
        "user_profiles": [
            "Aplicacion",
            "ADMINISTRADOR",
            "EDITOR",
            "PUBLICADOR",
            "Usuario"
        ],
        "user_roles": [
            "PUBLICADOR",
            "ADMINISTRADOR",
            "RuleInstall"
        ]
    },
    {
        "path": "/rulz/uninstall/publication/*",
        "user_profiles": [
            "Aplicacion",
            "ADMINISTRADOR",
            "EDITOR",
            "PUBLICADOR",
            "Usuario"
        ],
        "user_roles": [
            "PUBLICADOR",
            "ADMINISTRADOR",
            "RuleInstall"
        ]
    },
    {
        "path": "/snapshot/get/all",
        "user_profiles": [
            "ADMINISTRADOR",
            "EDITOR",
            "PUBLICADOR",
            "Usuario"
        ],
        "user_roles": [
            "PUBLICADOR",
            "ADMINISTRADOR",
            "EDITOR"
        ]
    },
    {
        "path": "/snapshot/export",
        "user_profiles": [
            "ADMINISTRADOR",
            "EDITOR",
            "PUBLICADOR",
            "Usuario"
        ],
        "user_roles": [
            "PUBLICADOR",
            "ADMINISTRADOR",
            "EDITOR"
        ]
    },
    {
        "path": "/snapshot/export/*",
        "user_profiles": [
            "ADMINISTRADOR",
            "EDITOR",
            "PUBLICADOR",
            "Usuario"
        ],
        "user_roles": [
            "PUBLICADOR",
            "ADMINISTRADOR",
            "EDITOR"
        ]
    },
    {
        "path": "/snapshot/import",
        "user_profiles": [
            "ADMINISTRADOR",
            "EDITOR",
            "PUBLICADOR",
            "Usuario"
        ],
        "user_roles": [
            "PUBLICADOR",
            "ADMINISTRADOR",
            "EDITOR"
        ]
    },
    {
        "path": "/snapshot/create/*",
        "user_profiles": [
            "ADMINISTRADOR",
            "EDITOR",
            "PUBLICADOR",
            "Usuario"
        ],
        "user_roles": [
            "PUBLICADOR",
            "ADMINISTRADOR",
            "EDITOR"
        ]
    },
    {
        "path": "/snapshot/use",
        "user_profiles": [
            "ADMINISTRADOR",
            "EDITOR",
            "PUBLICADOR",
            "Usuario"
        ],
        "user_roles": [
            "PUBLICADOR",
            "ADMINISTRADOR",
            "EDITOR"
        ]
    },
    {
        "path": "/snapshot/delete/*",
        "user_profiles": [
            "ADMINISTRADOR",
            "EDITOR",
            "PUBLICADOR",
            "Usuario"
        ],
        "user_roles": [
            "PUBLICADOR",
            "ADMINISTRADOR",
            "EDITOR"
        ]
    },
    {
        "path": "/snapshot/edit/*",
        "user_profiles": [
            "ADMINISTRADOR",
            "EDITOR",
            "PUBLICADOR",
            "Usuario"
        ],
        "user_roles": [
            "PUBLICADOR",
            "ADMINISTRADOR",
            "EDITOR"
        ]
    },
    {
        "path": "/rulz/drls_new",
        "user_profiles": [
            "ADMINISTRADOR",
            "EDITOR",
            "PUBLICADOR",
            "Usuario"
        ],
        "user_roles": [
            "PUBLICADOR",
            "ADMINISTRADOR",
            "EDITOR"
        ]
    },
    {
        "path": "/rulz/drls",
        "user_profiles": [
            "ADMINISTRADOR",
            "EDITOR",
            "PUBLICADOR",
            "Usuario"
        ],
        "user_roles": [
            "PUBLICADOR",
            "ADMINISTRADOR",
            "EDITOR"
        ]
    },
    {
        "path": "/rulz/drls/*/*",
        "user_profiles": [
            "ADMINISTRADOR",
            "EDITOR",
            "PUBLICADOR",
            "Usuario"
        ],
        "user_roles": [
            "PUBLICADOR",
            "ADMINISTRADOR",
            "EDITOR"
        ]
    },
    {
        "path": "/rulz/test",
        "user_profiles": [
            "Aplicacion",
            "ADMINISTRADOR",
            "EDITOR",
            "PUBLICADOR",
            "Usuario"
        ],
        "user_roles": [
            "PUBLICADOR",
            "ADMINISTRADOR",
            "EDITOR",
            "RuleSimulate"
        ]
    },
    {
        "path": "/rulz/test/data",
        "user_profiles": [
            "Aplicacion",
            "ADMINISTRADOR",
            "EDITOR",
            "PUBLICADOR",
            "Usuario"
        ],
        "user_roles": [
            "PUBLICADOR",
            "ADMINISTRADOR",
            "EDITOR",
            "RuleSimulate"
        ]
    },
    {
        "path": "/rulz/test/install",
        "user_profiles": [
            "Aplicacion",
            "ADMINISTRADOR",
            "EDITOR",
            "PUBLICADOR",
            "Usuario"
        ],
        "user_roles": [
            "PUBLICADOR",
            "ADMINISTRADOR",
            "RuleInstall"
        ]
    },
    {
        "path": "/rulz/test/uninstall",
        "user_profiles": [
            "Aplicacion",
            "ADMINISTRADOR",
            "EDITOR",
            "PUBLICADOR",
            "Usuario"
        ],
        "user_roles": [
            "PUBLICADOR",
            "ADMINISTRADOR",
            "RuleInstall"
        ]
    },
    {
        "path": "/rulz/test/list",
        "user_profiles": [
            "Aplicacion",
            "ADMINISTRADOR",
            "EDITOR",
            "PUBLICADOR",
            "Usuario"
        ],
        "user_roles": [
            "PUBLICADOR",
            "ADMINISTRADOR",
            "EDITOR",
            "ReadPublication"
        ]
    },
    {
        "path": "/rulz/install/*",
        "user_profiles": [
            "Aplicacion",
            "ADMINISTRADOR",
            "EDITOR",
            "PUBLICADOR",
            "Usuario"
        ],
        "user_roles": [
            "PUBLICADOR",
            "ADMINISTRADOR",
            "RuleInstall"
        ]
    },
    {
        "path": "/rulz/uninstall/*",
        "user_profiles": [
            "Aplicacion",
            "ADMINISTRADOR",
            "EDITOR",
            "PUBLICADOR",
            "Usuario"
        ],
        "user_roles": [
            "PUBLICADOR",
            "ADMINISTRADOR",
            "RuleInstall"
        ]
    },
    {
        "path": "/rulz/drl/rule",
        "user_profiles": [
            "Aplicacion",
            "ADMINISTRADOR",
            "EDITOR",
            "PUBLICADOR",
            "Usuario"
        ],
        "user_roles": [
            "PUBLICADOR",
            "ADMINISTRADOR",
            "EDITOR",
            "ReadRule"
        ]
    },
    {
        "path": "/rulz/drl/table",
        "user_profiles": [
            "Aplicacion",
            "ADMINISTRADOR",
            "EDITOR",
            "PUBLICADOR",
            "Usuario"
        ],
        "user_roles": [
            "PUBLICADOR",
            "ADMINISTRADOR",
            "EDITOR",
            "ReadTable"
        ]
    },
    {
        "path": "/rulz/drl/simulation",
        "user_profiles": [
            "Aplicacion",
            "ADMINISTRADOR",
            "EDITOR",
            "PUBLICADOR",
            "Usuario"
        ],
        "user_roles": [
            "PUBLICADOR",
            "ADMINISTRADOR",
            "EDITOR",
            "ReadSimulation"
        ]
    },
    {
        "path": "/rulz/files/*/*",
        "user_profiles": [
            "Aplicacion",
            "ADMINISTRADOR",
            "EDITOR",
            "PUBLICADOR",
            "Usuario"
        ],
        "user_roles": [
            "PUBLICADOR",
            "ADMINISTRADOR",
            "EDITOR",
            "WriteInstrument"
        ]
    },
    {
        "path": "/rulz/rule/all",
        "user_profiles": [
            "Aplicacion",
            "ADMINISTRADOR",
            "EDITOR",
            "PUBLICADOR",
            "Usuario"
        ],
        "user_roles": [
            "PUBLICADOR",
            "ADMINISTRADOR",
            "EDITOR",
            "ReadRule"
        ]
    },
    {
        "path": "/rulz/table/all",
        "user_profiles": [
            "Aplicacion",
            "ADMINISTRADOR",
            "EDITOR",
            "PUBLICADOR",
            "Usuario"
        ],
        "user_roles": [
            "PUBLICADOR",
            "ADMINISTRADOR",
            "EDITOR",
            "ReadTable"
        ]
    },
    {
        "path": "/rulz/catalog/all",
        "user_profiles": [
            "Aplicacion",
            "ADMINISTRADOR",
            "EDITOR",
            "PUBLICADOR",
            "Usuario"
        ],
        "user_roles": [
            "PUBLICADOR",
            "ADMINISTRADOR",
            "EDITOR",
            "ReadCatalog"
        ]
    },
    {
        "path": "/rulz/simulation/all",
        "user_profiles": [
            "Aplicacion",
            "ADMINISTRADOR",
            "EDITOR",
            "PUBLICADOR",
            "Usuario"
        ],
        "user_roles": [
            "PUBLICADOR",
            "ADMINISTRADOR",
            "EDITOR",
            "ReadSimulation"
        ]
    },
    {
        "path": "/rulz/entity/all",
        "user_profiles": [
            "Aplicacion",
            "ADMINISTRADOR",
            "EDITOR",
            "PUBLICADOR",
            "Usuario"
        ],
        "user_roles": [
            "PUBLICADOR",
            "ADMINISTRADOR",
            "EDITOR",
            "ReadEntity"
        ]
    },
    {
        "path": "/rulz/list/all",
        "user_profiles": [
            "Aplicacion",
            "ADMINISTRADOR",
            "EDITOR",
            "PUBLICADOR",
            "Usuario"
        ],
        "user_roles": [
            "PUBLICADOR",
            "ADMINISTRADOR",
            "EDITOR",
            "ReadList"
        ]
    },
    {
        "path": "/rulz/instrument/all",
        "user_profiles": [
            "Aplicacion",
            "ADMINISTRADOR",
            "EDITOR",
            "PUBLICADOR",
            "Usuario"
        ],
        "user_roles": [
            "PUBLICADOR",
            "ADMINISTRADOR",
            "EDITOR",
            "ReadInstrument"
        ]
    },
    {
        "path": "/rulz/function/all",
        "user_profiles": [
            "Aplicacion",
            "ADMINISTRADOR",
            "EDITOR",
            "PUBLICADOR",
            "Usuario"
        ],
        "user_roles": [
            "PUBLICADOR",
            "ADMINISTRADOR",
            "EDITOR",
            "ReadFunction"
        ]
    },
    {
        "path": "/rulz/formula/all",
        "user_profiles": [
            "Aplicacion",
            "ADMINISTRADOR",
            "EDITOR",
            "PUBLICADOR",
            "Usuario"
        ],
        "user_roles": [
            "PUBLICADOR",
            "ADMINISTRADOR",
            "EDITOR",
            "ReadFormula"
        ]
    },
    {
        "path": "/rulz/publication/all",
        "user_profiles": [
            "Aplicacion",
            "ADMINISTRADOR",
            "EDITOR",
            "PUBLICADOR",
            "Usuario"
        ],
        "user_roles": [
            "PUBLICADOR",
            "ADMINISTRADOR",
            "EDITOR",
            "ReadPublication"
        ]
    },
    {
        "path": "/rulz/rule/remove",
        "user_profiles": [
            "Aplicacion",
            "ADMINISTRADOR",
            "EDITOR",
            "PUBLICADOR",
            "Usuario"
        ],
        "user_roles": [
            "PUBLICADOR",
            "ADMINISTRADOR",
            "EDITOR",
            "WriteRule"
        ]
    },
    {
        "path": "/rulz/table/remove",
        "user_profiles": [
            "Aplicacion",
            "ADMINISTRADOR",
            "EDITOR",
            "PUBLICADOR",
            "Usuario"
        ],
        "user_roles": [
            "PUBLICADOR",
            "ADMINISTRADOR",
            "EDITOR",
            "WriteTable"
        ]
    },
    {
        "path": "/rulz/catalog/remove",
        "user_profiles": [
            "Aplicacion",
            "ADMINISTRADOR",
            "EDITOR",
            "PUBLICADOR",
            "Usuario"
        ],
        "user_roles": [
            "PUBLICADOR",
            "ADMINISTRADOR",
            "EDITOR",
            "WriteCatalog"
        ]
    },
    {
        "path": "/rulz/simulation/remove",
        "user_profiles": [
            "Aplicacion",
            "ADMINISTRADOR",
            "EDITOR",
            "PUBLICADOR",
            "Usuario"
        ],
        "user_roles": [
            "PUBLICADOR",
            "ADMINISTRADOR",
            "EDITOR",
            "WriteSimulation"
        ]
    },
    {
        "path": "/rulz/entity/remove",
        "user_profiles": [
            "Aplicacion",
            "ADMINISTRADOR",
            "EDITOR",
            "PUBLICADOR",
            "Usuario"
        ],
        "user_roles": [
            "PUBLICADOR",
            "ADMINISTRADOR",
            "EDITOR",
            "WriteEntity"
        ]
    },
    {
        "path": "/rulz/list/remove",
        "user_profiles": [
            "Aplicacion",
            "ADMINISTRADOR",
            "EDITOR",
            "PUBLICADOR",
            "Usuario"
        ],
        "user_roles": [
            "PUBLICADOR",
            "ADMINISTRADOR",
            "EDITOR",
            "WriteList"
        ]
    },
    {
        "path": "/rulz/instrument/remove",
        "user_profiles": [
            "Aplicacion",
            "ADMINISTRADOR",
            "EDITOR",
            "PUBLICADOR",
            "Usuario"
        ],
        "user_roles": [
            "PUBLICADOR",
            "ADMINISTRADOR",
            "EDITOR",
            "WriteInstrument"
        ]
    },
    {
        "path": "/rulz/function/remove",
        "user_profiles": [
            "Aplicacion",
            "ADMINISTRADOR",
            "EDITOR",
            "PUBLICADOR",
            "Usuario"
        ],
        "user_roles": [
            "PUBLICADOR",
            "ADMINISTRADOR",
            "EDITOR",
            "WriteFunction"
        ]
    },
    {
        "path": "/rulz/formula/remove",
        "user_profiles": [
            "Aplicacion",
            "ADMINISTRADOR",
            "EDITOR",
            "PUBLICADOR",
            "Usuario"
        ],
        "user_roles": [
            "PUBLICADOR",
            "ADMINISTRADOR",
            "EDITOR",
            "WriteFormula"
        ]
    },
    {
        "path": "/rulz/publication/remove",
        "user_profiles": [
            "Aplicacion",
            "ADMINISTRADOR",
            "EDITOR",
            "PUBLICADOR",
            "Usuario"
        ],
        "user_roles": [
            "PUBLICADOR",
            "ADMINISTRADOR",
            "EDITOR",
            "WritePublication"
        ]
    },
    {
        "path": "/rulz/drls/remove",
        "user_profiles": [
            "Aplicacion",
            "ADMINISTRADOR",
            "EDITOR",
            "PUBLICADOR",
            "Usuario"
        ],
        "user_roles": [
            "PUBLICADOR",
            "ADMINISTRADOR",
            "EDITOR",
            "WritePublication"
        ]
    },
    {
        "path": "/rulz/*/notincatalog",
        "user_profiles": [
            "Aplicacion",
            "ADMINISTRADOR",
            "EDITOR",
            "PUBLICADOR",
            "Usuario"
        ],
        "user_roles": [
            "PUBLICADOR",
            "ADMINISTRADOR",
            "EDITOR",
            "ReadRule",
            "ReadTable",
            "ReadCatalog"
        ]
    },
    {
        "path": "/rulz/rule/*",
        "user_profiles": [
            "Aplicacion",
            "ADMINISTRADOR",
            "EDITOR",
            "PUBLICADOR",
            "Usuario"
        ],
        "user_roles": [
            "PUBLICADOR",
            "ADMINISTRADOR",
            "EDITOR",
            "ReadRule"
        ]
    },
    {
        "path": "/rulz/table/*",
        "user_profiles": [
            "Aplicacion",
            "ADMINISTRADOR",
            "EDITOR",
            "PUBLICADOR",
            "Usuario"
        ],
        "user_roles": [
            "PUBLICADOR",
            "ADMINISTRADOR",
            "EDITOR",
            "ReadTable"
        ]
    },
    {
        "path": "/rulz/catalog/*",
        "user_profiles": [
            "Aplicacion",
            "ADMINISTRADOR",
            "EDITOR",
            "PUBLICADOR",
            "Usuario"
        ],
        "user_roles": [
            "PUBLICADOR",
            "ADMINISTRADOR",
            "EDITOR",
            "ReadCatalog"
        ]
    },
    {
        "path": "/rulz/simulation/*",
        "user_profiles": [
            "Aplicacion",
            "ADMINISTRADOR",
            "EDITOR",
            "PUBLICADOR",
            "Usuario"
        ],
        "user_roles": [
            "PUBLICADOR",
            "ADMINISTRADOR",
            "EDITOR",
            "ReadSimulation"
        ]
    },
    {
        "path": "/rulz/entity/*",
        "user_profiles": [
            "Aplicacion",
            "ADMINISTRADOR",
            "EDITOR",
            "PUBLICADOR",
            "Usuario"
        ],
        "user_roles": [
            "PUBLICADOR",
            "ADMINISTRADOR",
            "EDITOR",
            "ReadEntity"
        ]
    },
    {
        "path": "/rulz/list/*",
        "user_profiles": [
            "Aplicacion",
            "ADMINISTRADOR",
            "EDITOR",
            "PUBLICADOR",
            "Usuario"
        ],
        "user_roles": [
            "PUBLICADOR",
            "ADMINISTRADOR",
            "EDITOR",
            "ReadList"
        ]
    },
    {
        "path": "/rulz/instrument/*",
        "user_profiles": [
            "Aplicacion",
            "ADMINISTRADOR",
            "EDITOR",
            "PUBLICADOR",
            "Usuario"
        ],
        "user_roles": [
            "PUBLICADOR",
            "ADMINISTRADOR",
            "EDITOR",
            "ReadInstrument"
        ]
    },
    {
        "path": "/rulz/function/*",
        "user_profiles": [
            "Aplicacion",
            "ADMINISTRADOR",
            "EDITOR",
            "PUBLICADOR",
            "Usuario"
        ],
        "user_roles": [
            "PUBLICADOR",
            "ADMINISTRADOR",
            "EDITOR",
            "ReadFunction"
        ]
    },
    {
        "path": "/rulz/formula/*",
        "user_profiles": [
            "Aplicacion",
            "ADMINISTRADOR",
            "EDITOR",
            "PUBLICADOR",
            "Usuario"
        ],
        "user_roles": [
            "PUBLICADOR",
            "ADMINISTRADOR",
            "EDITOR",
            "ReadFormula"
        ]
    },
    {
        "path": "/rulz/publication/*",
        "user_profiles": [
            "Aplicacion",
            "ADMINISTRADOR",
            "EDITOR",
            "PUBLICADOR",
            "Usuario"
        ],
        "user_roles": [
            "PUBLICADOR",
            "ADMINISTRADOR",
            "EDITOR",
            "ReadPublication"
        ]
    },
    {
        "path": "/auditory/registered_users",
        "user_profiles": [
            "ADMINISTRADOR",
            "Usuario"
        ],
        "user_roles": [
            "ADMINISTRADOR"
        ]
    },
    {
        "path": "/auditory/search",
        "user_profiles": [
            "ADMINISTRADOR",
            "Usuario"
        ],
        "user_roles": [
            "ADMINISTRADOR"
        ]
    },
    {
        "path": "/auditory/getdata/*",
        "user_profiles": [
            "ADMINISTRADOR",
            "Usuario"
        ],
        "user_roles": [
            "ADMINISTRADOR"
        ]
    },
    {
        "path": "/auditory/getregistry/*",
        "user_profiles": [
            "ADMINISTRADOR",
            "Usuario"
        ],
        "user_roles": [
            "ADMINISTRADOR"
        ]
    },
    {
        "path": "/api/register_key",
        "user_profiles": [
            "ADMINISTRADOR",
            "Usuario"
        ],
        "user_roles": [
            "ADMINISTRADOR"
        ]
    },
    {
        "path": "/api/all_keys",
        "user_profiles": [
            "ADMINISTRADOR",
            "Usuario"
        ],
        "user_roles": [
            "ADMINISTRADOR"
        ]
    },
    {
        "path": "/api/delete_key/*",
        "user_profiles": [
            "ADMINISTRADOR",
            "Usuario"
        ],
        "user_roles": [
            "ADMINISTRADOR"
        ]
    },
    {
        "path": "/rulz/count/*",
        "user_profiles": [
            "ADMINISTRADOR",
            "EDITOR",
            "PUBLICADOR",
            "Usuario"
        ],
        "user_roles": [
            "PUBLICADOR",
            "ADMINISTRADOR",
            "EDITOR"
        ]
    }
]
FUNCIONALITY_ROLES_MATRIX = [('MENU_PUBLICACION', ['ADMINISTRADOR', 'PUBLICADOR']), ('AUDIT_MENU', ['ADMINISTRADOR']), ('BTN_PUBLICAR_ESCENARIO', ['ADMINISTRADOR', 'PUBLICADOR']), ('DELETE_SNAPSHOT', ['ADMINISTRADOR']), ('CONFIG_MENU', ['ADMINISTRADOR'])]


def customParseGoogle(s):
    d = json.loads(s)
    for k, v in d.items():
        if not isinstance(k, bytes) and not isinstance(v, bytes):
            continue
        d.pop(k)
        if isinstance(k, bytes):
            k = k.decode('utf-8')
        if isinstance(v, bytes):
            v = v.decode('utf-8')
        d[k] = v
    return d


def parseGoogleData(me):
    return json.loads(me.__dict__['_content'])


class OAuthSignIn(object):
    providers = None

    def __init__(self, provider_name):
        self.provider_name = provider_name
        credentials = current_app.config['OAUTH_CREDENTIALS'][provider_name]
        self.consumer_id = credentials['id']
        self.consumer_secret = credentials['secret']

    def authorize(self):
        pass

    def callback(self):
        pass

    def get_callback_url(self):
        return url_for('security.oauth_callback', provider=self.provider_name,
                       _external=True)

    @classmethod
    def get_provider(self, provider_name):
        if self.providers is None:
            self.providers = {}
            for provider_class in self.__subclasses__():
                provider = provider_class()
                self.providers[provider.provider_name] = provider
        return self.providers[provider_name]


class FacebookSignIn(OAuthSignIn):
    def __init__(self):
        super(FacebookSignIn, self).__init__('facebook')
        self.service = OAuth2Service(
            name='facebook',
            client_id=self.consumer_id,
            client_secret=self.consumer_secret,
            authorize_url='https://graph.facebook.com/oauth/authorize',
            access_token_url='https://graph.facebook.com/oauth/access_token',
            base_url='https://graph.facebook.com/'
        )

    def authorize(self):
        return redirect(self.service.get_authorize_url(
            scope='email',
            response_type='code',
            redirect_uri=self.get_callback_url())
        )

    def callback(self):
        if 'code' not in request.args:
            return None, None, None
        oauth_session = self.service.get_auth_session(
            data={'code': request.args['code'],
                  'grant_type': 'authorization_code',
                  'redirect_uri': self.get_callback_url()}
        )
        me = oauth_session.get('me?fields=name,id,email').json()
        return (
            'facebook$' + me['id'],
            me.get('name'),  # Facebook does not provide username, so the email's user is used instead
            me.get('email'),
            me.get('email').split('@')[1].split('.', 1)[0]
        )


class GoogleSignIn(OAuthSignIn):
    def __init__(self):
        super(GoogleSignIn, self).__init__('google')
        self.service = OAuth2Service(
            name='google',
            client_id=self.consumer_id,
            client_secret=self.consumer_secret,
            authorize_url='https://accounts.google.com/o/oauth2/auth',
            access_token_url='https://accounts.google.com/o/oauth2/token',
            base_url='https://www.google.com/accounts/'
        )

    def authorize(self):
        return redirect(self.service.get_authorize_url(
            scope='https://www.googleapis.com/auth/userinfo.email https://www.googleapis.com/auth/userinfo.profile',
            response_type='code',
            redirect_uri=self.get_callback_url())
        )

    def callback(self):
        if 'code' not in request.args:
            return None, None, None
        oauth_session = self.service.get_auth_session(
            data={'code': request.args['code'],
                  'grant_type': 'authorization_code',
                  'redirect_uri': self.get_callback_url()},
            decoder=customParseGoogle
        )
        me = parseGoogleData(oauth_session.get('https://www.googleapis.com/oauth2/v1/userinfo', params={'format': 'json'}))
        current_app.logger.debug(me)
        g_hd = 'google_user'

        if me.get('hd') is not None:
            g_hd = me.get('hd').split('.', 1)[0]

        return (
            'google$' + me['id'],
            me.get('name'),
            me.get('email'),
            g_hd
        )


class TwitterSignIn(OAuthSignIn):
    def __init__(self):
        super(TwitterSignIn, self).__init__('twitter')
        self.service = OAuth1Service(
            name='twitter',
            consumer_key=self.consumer_id,
            consumer_secret=self.consumer_secret,
            request_token_url='https://api.twitter.com/oauth/request_token',
            authorize_url='https://api.twitter.com/oauth/authorize',
            access_token_url='https://api.twitter.com/oauth/access_token',
            base_url='https://api.twitter.com/1.1/'
        )

    def authorize(self):
        request_token = self.service.get_request_token(
            params={'security.oauth_callback': self.get_callback_url()}
        )
        session['request_token'] = request_token
        return redirect(self.service.get_authorize_url(request_token[0]))

    def callback(self):
        request_token = session.pop('request_token')
        if 'oauth_verifier' not in request.args:
            return None, None, None
        oauth_session = self.service.get_auth_session(
            request_token[0],
            request_token[1],
            data={'oauth_verifier': request.args['oauth_verifier']}
        )
        me = oauth_session.get('account/verify_credentials.json').json()
        social_id = 'twitter$' + str(me.get('id'))
        username = me.get('screen_name')
        return social_id, username, 'none', 'twitter_user'
