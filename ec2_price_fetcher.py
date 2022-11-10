import boto3
import json
import io
from multiprocessing.pool import ThreadPool as Pool
import argparse

SERVICE_CODE = 'AmazonEC2'
PRODUCT_FAMILY = 'Compute Instance'

def upload(s3, bucket_name, p,i,partition):
    product = json.loads(p)
    f = io.BytesIO(p.encode())
    object_key = '{}/{}.offerfile.json'.format(partition, product['product']['sku'])
    s3.upload_fileobj(f, bucket_name, object_key)
    return '{} ({})'.format(object_key, i)
    
def success(sku): 
    print(sku)
    
def fail(e):
    print('Failed: {0}'.format((e)))
    
def main():
    
    parser = argparse.ArgumentParser(
        prog = 'EC2 Price Fetcher',
        description = 'Fetches offer files for EC2 instance pricing from the AWS Pricing API and writes them to S3')
        
    parser.add_argument('bucket_name')
    parser.add_argument('-r', '--s3_region', default='us-east-1')
    args = parser.parse_args()
    
    if not args.bucket_name:
        return parser.usage()
    
    client = boto3.client('pricing', region_name='us-east-1')
    s3 = boto3.client('s3', region_name=args.s3_region)
    
    filters = [
        {
            'Type': 'TERM_MATCH',
            'Field': 'productFamily',
            'Value': PRODUCT_FAMILY
        }
    ]
    
    paginator = client.get_paginator('get_products')
    page_iterator = paginator.paginate(
        ServiceCode = SERVICE_CODE,
        Filters = filters)
        
    i = 0
    with Pool(processes=20) as pool:
        for page in page_iterator:
            for p in page['PriceList']:
                i += 1
                partition = (i%25) + 1
                pool.apply_async(upload, (s3,args.bucket_name,p,i,partition), {}, success, fail)
                
if __name__ == '__main__':
    main()
