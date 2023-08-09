import CloudFlare
from requests import get

def pub_ip():
    ip = get('https://api.ipify.org').content.decode('utf8')
    print('My public IP address is: {}'.format(ip))
    return(ip)

me = pub_ip()

def update(dn):
    zone_name = dn

    cf = CloudFlare.CloudFlare(token=open(".secret").read().strip())

    # query for the zone name and expect only one value back
    try:
        zones = cf.zones.get(params = {'name':zone_name,'per_page':1})
    except CloudFlare.exceptions.CloudFlareAPIError as e:
        exit('/zones.get %d %s - api call failed' % (e, e))
    except Exception as e:
        exit('/zones.get - %s - api call failed' % (e))

    if len(zones) == 0:
        exit('No zones found')

    # extract the zone_id which is needed to process that zone
    zone = zones[0]
    zone_id = zone['id']

    # request the DNS records from that zone
    try:
        dns_records = cf.zones.dns_records.get(zone_id)
    except CloudFlare.exceptions.CloudFlareAPIError as e:
        exit('/zones/dns_records.get %d %s - api call failed' % (e, e))

    # print the results - first the zone name
    # print("zone_id=%s zone_name=%s" % (zone_id, zone_name))

    # then all the DNS records for that zone
    for dns_record in dns_records:
        r_name = dns_record['name']

        r_type = dns_record['type']

        r_value = dns_record['content']

        r_id = dns_record['id']

        if r_type == "A":
            if r_value != me:
                print(f"Updating {r_name} because it has '{r_value}' instead of '{me}'.")
                cf.zones.dns_records.post(zone_id, data={'name':r_name, 'type':'A', 'content': me})
            else:
                print(f"Record {r_name} is unchanged.")


domains = ['xhec.dev', 'mattcompton.dev']

for domain in domains:
    update(domain)