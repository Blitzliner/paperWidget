from fastapi import FastAPI, Request, Form, UploadFile, File, HTTPException, status
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os
import widget
import utils
from config import config

logger = utils.getLogger()

app = FastAPI()

templates = Jinja2Templates(directory="templates")  # Ensure your template.html is in the 'templates' directory


@app.get('/', response_class=HTMLResponse)
async def get_website(request: Request):
    logger.info('Create main website')
    return templates.TemplateResponse('template.html',
                                      {'request': request, 'apps': config.apps, 'active_app': config.active_app})


@app.post('/upload')
async def upload_file(request: Request, upload: UploadFile = File(...)):
    upload_image_path = os.path.join(os.path.dirname(__file__), 'upload.png')
    try:
        with open(upload_image_path, 'wb') as file:
            file.write(await upload.read())
        logger.info(f'Upload image to {upload_image_path}')
        widget.update(upload_image_path)
    except Exception as e:
        logger.error(f'File upload failed: {e}', exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail='File upload failed')
    # return {'message': 'File uploaded successfully'}
    return await get_website(request)


@app.post('/apps/{app_id}')
async def handle_app_form(app_id: str, request: Request):
    form_data = await request.form()
    fields = {key: value for key, value in form_data.items()}
    logger.info(f'Received form data for app_id={app_id}: {fields}')

    app = config.get_app(app_id)
    if app:
        app.parameter = fields
        app.general = fields
    else:
        logger.warning(f'Invalid App Requested! app_id: {app_id}')
        raise HTTPException(status_code=404, detail='App not found')

    return await get_website(request)


@app.post('/general')
async def handle_general_form(request: Request, active_app: str = Form(None), save: str = Form(None), update: str = Form(None)):
    if save:
        logger.info('Button pressed in form "general"->"save"')
        config.active_app = active_app
    elif update:
        logger.info('Button pressed in form "general"->"update"')
        widget.update()
    else:
        logger.warning('Unexpected button pressed in form "general"!')

    return await get_website(request)


# Static files (optional, for serving styles or other assets)
app.mount('/static', StaticFiles(directory='templates/static'), name='static')

if __name__ == '__main__':
    import uvicorn

    port = 8000
    logger.info(f'Open Browser: {utils.get_network_ip()}:{port}')
    uvicorn.run(app, host='0.0.0.0', port=port)
