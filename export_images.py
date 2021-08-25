import fiona
import rasterio
from rasterio.mask import mask

regions = ['austin', 'dallas', 'elpaso', 'gulf', 'houston', 'waco']
# regions = ['amarillo', 'lubbock', 'beaumont', 'corpus_christi', 'odessa', 'bryan']

year = 2016
while year <= 2016:
    for region in regions:
        with fiona.open(f'{region}_houses.shp') as shapefile:
            geoms = [feature['geometry'] for feature in shapefile]
            ids = [feature['properties']['id'] for feature in shapefile]
        with rasterio.open(f'sentinel_{year}_{region}.vrt') as src:
            print(len(geoms))
            for i in range(len(geoms)):
                if i % 10000 == 0:
                    print(i)
                out_img, out_transform = mask(src, geoms[i:i + 1], crop=True)
                out_meta = src.meta.copy()
                out_meta.update({
                    'driver': 'GTiff', 
                    'height': out_img.shape[1],
                    'width' : out_img.shape[2],
                    'transform': out_transform
                })

                with rasterio.open('sentinel_grid2/{}_{}_{}.tif'.format(year, ids[i], region), 'w', **out_meta) as dest:
                    dest.write(out_img)
    
        print(f'finished {region}')
    print(f'finished {year}')
    year += 1
