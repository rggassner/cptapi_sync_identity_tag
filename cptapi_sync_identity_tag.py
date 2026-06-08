#!venv/bin/python3
import sys
import ldap
import ldap.filter
from cptapi import Cptapi
import requests
from my_config import *

#domain_name=''
domain=Cptapi(user,password,url,domain_name,api_wait_time=api_wait_time,read_only=False,page_size=page_size,publish_wait_time=publish_wait_time)

if __name__ == "__main__":
    # LDAP Connection Parameters
    LDAP_HOST = 'ldap.host'
    LDAP_PORT = 636
    LDAP_SEARCH_BASE = 'dc=com,dc=br'
    LDAP_SCOPE = ldap.SCOPE_SUBTREE
    LDAP_TIMEOUT = 600

    LDAP_SEARCH_FILTER = '(cn=group-*identity-tag*)'

    print(f"Connecting to LDAP server: {LDAP_HOST}:{LDAP_PORT}")
    print(f"Searching base DN: '{LDAP_SEARCH_BASE}'")
    print(f"Using filter: '{LDAP_SEARCH_FILTER}'\n")

    ldap_connection = None
    try:
        # Initialize connection
        ldap_connection = ldap.initialize(f"ldaps://{LDAP_HOST}:{LDAP_PORT}")
        ldap_connection.set_option(ldap.OPT_REFERRALS, 0)
        ldap_connection.set_option(ldap.OPT_PROTOCOL_VERSION, ldap.VERSION3)
        ldap_connection.set_option(ldap.OPT_NETWORK_TIMEOUT, LDAP_TIMEOUT)

        # Perform the search requesting only the 'cn' attribute to minimize network load
        group_results = ldap_connection.search_s(
            LDAP_SEARCH_BASE,
            LDAP_SCOPE,
            LDAP_SEARCH_FILTER,
            attrlist=['cn']
        )

        print(f"--- Found {len(group_results)} matching groups ---")

        # Iterate and print the group names
        for dn, attrs in group_results:
            # Check if 'cn' exists in the entry attributes
            if 'cn' in attrs:
                for cn_value in attrs['cn']:
                    # Decode from bytes to string safely
                    try:
                        group_name = cn_value.decode('utf-8') if isinstance(cn_value, bytes) else str(cn_value)
                        domain.add_identity_tag(name="EXT_ID_"+group_name,external_identifier="EXT_ID_"+group_name,color="green")
                        print("EXT_ID_"+group_name)
                    except UnicodeDecodeError:
                        print(f"[Error decoding CN for DN: {dn}]")
        domain.publish()
        domain.logout()


    except ldap.SERVER_DOWN as e:
        print(f"LDAP Error: Could not connect to the LDAP server. Error: {e}")
        sys.exit(1)
    except ldap.NO_SUCH_OBJECT as e:
        print(f"LDAP Error: Search base '{LDAP_SEARCH_BASE}' not found. Error: {e}")
        sys.exit(1)
    except ldap.LDAPError as e:
        print(f"An LDAP error occurred: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        sys.exit(1)
    finally:
        if ldap_connection:
            ldap_connection.unbind_s()
            print("\nDisconnected from LDAP server.")

