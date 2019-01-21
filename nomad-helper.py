import nomad
import os
import argparse
import datetime
import time

key_path = '/home/muman/keys/ssl'


def dump_jobs(host=None, cert_path=None):
    """
    Dump all jobs and allocation logs on this host using the path passed for certificates.

    :param host:
    :param cert_path:
    :return:
    """
    cert_files = {
        'CA': os.path.join(cert_path, 'ca.pem'),
        'CRT': os.path.join(cert_path, 'client.crt'),
        'KEY': os.path.join(cert_path, 'client.key')
    }

    my_nomad = nomad.Nomad(host=host, secure=True, verify=cert_files['CA'],
                           cert=(cert_files['CRT'], cert_files['KEY']))

    for job in my_nomad.jobs:
        submit_time=time.strftime('%Y-%m-%d %I:%M:%S%p', time.localtime(job['SubmitTime']/1000000000))
#        print(submit_time)

        print('=' * 80)
        print("JOB ID : {:50s} STATUS : {:12s} SUBMITTED : {}".format(job['ID'], job['Status'], submit_time))

        allocations = my_nomad.job.get_allocations(job["ID"])
        if allocations:
            print("ALLOCATIONS:")

            # Iterate through all allocations

            for allocation in allocations:
                print(">> ALLOCATION ID : {} ALLOCATION NAME : {}".format(allocation['ID'], allocation['Name']))

                alloc_id = allocation['ID']
                task_id = list(allocation['TaskStates'].keys())[0] #  allocation['JobID']

                try:
                    stderr_log = my_nomad.client.stream_logs.stream(id=alloc_id, task=task_id, type='stderr', plain=True)
                    print('-- LOG', '-' * 74)
                    print(stderr_log)
                    print('-' * 80)
                except Exception as e:
                    print("EXCEPTION: {}".format(e))


def main():
    parser = argparse.ArgumentParser(prog='nomad-helper', description='Dump all nomad logs')

    parser.add_argument("--host", action='store', dest='nomad_host',
                        default=os.getenv('NOMAD_HOST', '10.13.0.6'))
    parser.add_argument("--cert-path", action='store', dest='cert_path',
                        default=os.getenv('NOMAD_CERT_PATH', key_path))

    options = parser.parse_args()

    dump_jobs(host=options.nomad_host, cert_path=options.cert_path)


if __name__ == '__main__':
    main()

